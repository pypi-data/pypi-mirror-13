import numpy as np
cimport numpy as np
from libc.math cimport sqrt, pow, exp
from libc.stdio cimport printf
from libc.stdlib cimport exit
from cython.parallel import prange
cimport cython
cimport openmp

class SCFNotConverged(Exception):
    def __init__(self, residual, threshold):
        self.residual = residual
        self.threshold = threshold


#This part os modified for the thole model
@cython.boundscheck( False )
def dipole_coupling_tensor_thole_cython(
        np.ndarray[long,ndim=1]particles,
        np.ndarray[double,ndim=2]_r,
        np.ndarray[double,ndim=3]_a0,
        int num_threads = 1
        ):
    cdef int i, j
    cdef int n = particles.shape[0]
    cdef np.ndarray[double, ndim = 4] _T = np.zeros((n, 3, n,  3))
    cdef double rx, ry, rz
    cdef double dr, dr2, term
    cdef double t_xx, t_xy, t_xz, t_yx, t_yy, t_yz, t_zx, t_zy, t_zz

#Variables for calculating the damping
    cdef double a_trace_p, a_trace_o, fv, fe, ft, v, u, a
    cdef double damp = 2.1304 



    for i in prange( n, nogil = True, num_threads = num_threads ):
        for j in range(i):
            if particles[i] == particles[j]:
                continue
            rx = _r[j, 0] - _r[i, 0]
            ry = _r[j, 1] - _r[i, 1]
            rz = _r[j, 2] - _r[i, 2]

#This is the distance using norm using clib.math.sqrt
            dr2 = rx*rx + ry*ry + rz*rz
            dr = sqrt( dr2 )

#Define damping params, v, fv = d_mono, fe, ft
            a_trace_p = (_a0[ i, 0, 0] + _a0[ i, 1, 1] +_a0[ i, 2, 2] )/3.0
            a_trace_o = (_a0[ j, 0, 0] + _a0[ j, 1, 1] +_a0[ j, 2, 2] )/3.0
            
            u = dr / pow (( a_trace_p * a_trace_o ), 1.0/6.0 )
            v = damp * u
            fv =  1.0 - (( 0.5 * v + 1) * exp(-v))
            fe = fv - (( 0.5 * pow(v, 2) + 0.5 * v) * exp(-v))
            ft = fe - ( pow(v, 3.0) * exp( -v ) / 6.0)


            t_xx = ( 3*rx*rx*ft - fe*dr2)/ pow(dr2, 2.5 )
            t_xy = ( 3*rx*ry*ft )/ pow(dr2, 2.5 )
            t_xz = ( 3*rx*rz*ft )/ pow(dr2, 2.5 )

            t_yx = ( 3*ry*rx*ft )/ pow(dr2, 2.5 )
            t_yy = ( 3*ry*ry*ft - fe*dr2)/ pow(dr2, 2.5 )
            t_yz = ( 3*ry*rz*ft )/ pow(dr2, 2.5 )

            t_zx = ( 3*rz*rx*ft )/ pow(dr2, 2.5 )
            t_zy = ( 3*rz*ry*ft )/ pow(dr2, 2.5 )
            t_zz = ( 3*rz*rz*ft - fe*dr2)/ pow(dr2, 2.5 )

            _T[ i, 0, j, 0 ] = t_xx
            _T[ i, 0, j, 1 ] = t_xy
            _T[ i, 0, j, 2 ] = t_xz

            _T[ i, 1, j, 0 ] = t_yx
            _T[ i, 1, j, 1 ] = t_yy
            _T[ i, 1, j, 2 ] = t_yz

            _T[ i, 2, j, 0 ] = t_zx
            _T[ i, 2, j, 1 ] = t_zy
            _T[ i, 2, j, 2 ] = t_zz

#permute i and j
            _T[ j, 0, i, 0 ] = t_xx
            _T[ j, 0, i, 1 ] = t_xy
            _T[ j, 0, i, 2 ] = t_xz

            _T[ j, 1, i, 0 ] = t_yx
            _T[ j, 1, i, 1 ] = t_yy
            _T[ j, 1, i, 2 ] = t_yz

            _T[ j, 2, i, 0 ] = t_zx
            _T[ j, 2, i, 1 ] = t_zy
            _T[ j, 2, i, 2 ] = t_zz
    return _T

#Thole model
@cython.boundscheck( False )
def solve_scf_for_external_thole_cython(
        np.ndarray[long,ndim=1]particles,
        np.ndarray[double,ndim=1]E,
        np.ndarray[double,ndim=2]_r,
        np.ndarray[double,ndim=1]_q,
        np.ndarray[double,ndim=2]_p0,
        np.ndarray[double,ndim=3]_a0,
        np.ndarray[double,ndim=4]_b0,
        np.ndarray[double,ndim=2]_field,
        int max_it = 100,
        double threshold = 1e-8,
        int num_threads = 1
        ):
    """An optimized version of solve_scf_for_external which explicitly takes
    arrays of the particles properties, and outputs the local field at each pointa
    after the residual is below threshold"""

    cdef int Nmax = particles.shape[0]

    cdef np.ndarray[double, ndim=2] E_p0 = np.zeros( (Nmax, 3))
    cdef np.ndarray[double, ndim=2] E_at_p = np.zeros( (Nmax, 3 ))
    cdef double[:,:] para_field = _field
    E_at_p[:, :] = _field

    cdef int i, o, p, k, j, l
    cdef double residual, dr, dr2, tmp_dr, tmp_x, tmp_y, tmp_z

#Tholes damping parameter 'a'
    cdef double damp = 2.1304

    cdef double rx, ry, rz
    cdef double px, py, pz

    cdef double ax, ay, az, bx, by, bz
#Variables for calculating the damping
    cdef double a_trace_p, a_trace_o, fv, fe, ft, v, u, a

#dipole components for particle o
    cdef double p_o_x, p_o_y, p_o_z

#monopole/dipole x, y, z component from particle o
    cdef double proj_o
    cdef double mx, my, mz
    cdef double dx, dy, dz
    cdef double tmp_E_x, tmp_E_y,tmp_E_z

    for i in range( max_it ):
#Parallelize over outer loop, over each particle p
        for p in prange( Nmax, num_threads = num_threads,
                nogil = True):
            tmp_E_x = 0
            tmp_E_y = 0
            tmp_E_z = 0
            for o in range( Nmax ):
                if particles[p] == particles[o]:
                    continue
                ax = 0
                ay = 0
                az = 0
                bx = 0
                by = 0
                bz = 0
                for k in range(3):
                    ax = ax + _a0[o, 0, k ] * E_at_p[o, k]
                    ay = ay + _a0[o, 1, k ] * E_at_p[o, k]
                    az = az + _a0[o, 2, k ] * E_at_p[o, k]
                    for j in range(3):
                        bx = bx + 0.5*(_b0[o, 0, k, j ] * E_at_p[o, k]* E_at_p[o, j])
                        by = by + 0.5*(_b0[o, 1, k, j ] * E_at_p[o, k]* E_at_p[o, j])
                        bz = bz + 0.5*(_b0[o, 2, k, j ] * E_at_p[o, k]* E_at_p[o, j])
                p_o_x = _p0[o, 0] + ax + bx
                p_o_y = _p0[o, 1] + ay + by
                p_o_z = _p0[o, 2] + az + bz


#Calculate distance vectors
                rx = _r[p, 0] - _r[o, 0]
                ry = _r[p, 1] - _r[o, 1]
                rz = _r[p, 2] - _r[o, 2]

#This is the distance using norm using clib.math.sqrt
                dr2 = rx*rx + ry*ry + rz*rz
                dr = sqrt( dr2 )
                #printf( "%f\n", dr )

#Define damping params, v, fv = d_mono, fe, ft
                a_trace_p = (_a0[ p, 0, 0] + _a0[ p, 1, 1] +_a0[ p, 2, 2] )/3.0
                a_trace_o = (_a0[ o, 0, 0] + _a0[ o, 1, 1] +_a0[ o, 2, 2] )/3.0
                
                u = dr / pow( ( a_trace_p * a_trace_o ), 1.0/6.0 )
                v = damp * u
                fv = 1 - (( 0.5 * v + 1) * exp(-v))
                fe = fv - (( 0.5 * pow(v,2.0) + 0.5 * v) * exp(-v))
                ft = fe - ( pow(v,3.0) * exp( -v ) / 6.0)
#
                mx = fe * _q[o] * rx / pow(dr2, 1.5 )
                my = fe * _q[o] * ry / pow(dr2, 1.5 )
                mz = fe * _q[o] * rz / pow(dr2, 1.5 )

                proj_o = rx*p_o_x + ry*p_o_y + rz*p_o_z

                dx = (3*rx*proj_o * ft - fe * dr2*p_o_x)/pow( dr2, 2.5 )
                dy = (3*ry*proj_o * ft - fe * dr2*p_o_y)/pow( dr2, 2.5 )
                dz = (3*rz*proj_o * ft - fe * dr2*p_o_z)/pow( dr2, 2.5 )

                tmp_E_x = tmp_E_x + mx + dx
                tmp_E_y = tmp_E_y + my + dy
                tmp_E_z = tmp_E_z + mz + dz

            _field[ p, 0] = tmp_E_x
            _field[ p, 1] = tmp_E_y
            _field[ p, 2] = tmp_E_z

            _field[ p, 0] = _field[ p, 0] + E[0]
            _field[ p, 1] = _field[ p, 1] + E[1]
            _field[ p, 2] = _field[ p, 2] + E[2]

        E_at_p[:, :] = _field
        residual = np.linalg.norm( E_p0 - E_at_p)
        #print residual, threshold
        if residual < threshold:
            return E_at_p, i, residual
        E_p0[:, :] = E_at_p
    raise SCFNotConverged(residual, threshold)

#This is the standard model for pointdipole without dampings
@cython.boundscheck( False )
def dipole_coupling_tensor_pointdipole_cython(
        np.ndarray[long,ndim=1]particles,
        np.ndarray[double,ndim=2]_r,
        int num_threads = 1
        ):
    cdef int i, j
    cdef int n = particles.shape[0]
    cdef np.ndarray[double, ndim = 4] _T = np.zeros((n, 3, n,  3))
    cdef double rx, ry, rz
    cdef double dr2, term
    cdef double t_xx, t_xy, t_xz, t_yx, t_yy, t_yz, t_zx, t_zy, t_zz

    for i in prange( n, nogil = True, num_threads = num_threads ):
        for j in range(i):
            if particles[i] == particles[j]:
                continue
            rx = _r[j, 0] - _r[i, 0]
            ry = _r[j, 1] - _r[i, 1]
            rz = _r[j, 2] - _r[i, 2]

            dr2 = rx*rx + ry*ry + rz*rz 

            t_xx = ( 3*rx*rx - dr2)/ pow(dr2, 2.5 )
            t_xy = ( 3*rx*ry )/ pow(dr2, 2.5 )
            t_xz = ( 3*rx*rz )/ pow(dr2, 2.5 )

            t_yx = ( 3*ry*rx )/ pow(dr2, 2.5 )
            t_yy = ( 3*ry*ry - dr2)/ pow(dr2, 2.5 )
            t_yz = ( 3*ry*rz )/ pow(dr2, 2.5 )

            t_zx = ( 3*rz*rx )/ pow(dr2, 2.5 )
            t_zy = ( 3*rz*ry )/ pow(dr2, 2.5 )
            t_zz = ( 3*rz*rz - dr2)/ pow(dr2, 2.5 )

            _T[ i, 0, j, 0 ] = t_xx
            _T[ i, 0, j, 1 ] = t_xy
            _T[ i, 0, j, 2 ] = t_xz

            _T[ i, 1, j, 0 ] = t_yx
            _T[ i, 1, j, 1 ] = t_yy
            _T[ i, 1, j, 2 ] = t_yz

            _T[ i, 2, j, 0 ] = t_zx
            _T[ i, 2, j, 1 ] = t_zy
            _T[ i, 2, j, 2 ] = t_zz

#permute i and j
            _T[ j, 0, i, 0 ] = t_xx
            _T[ j, 0, i, 1 ] = t_xy
            _T[ j, 0, i, 2 ] = t_xz

            _T[ j, 1, i, 0 ] = t_yx
            _T[ j, 1, i, 1 ] = t_yy
            _T[ j, 1, i, 2 ] = t_yz

            _T[ j, 2, i, 0 ] = t_zx
            _T[ j, 2, i, 1 ] = t_zy
            _T[ j, 2, i, 2 ] = t_zz
    return _T


 

@cython.boundscheck( False )
def solve_scf_for_external_pointdipole_cython(
        np.ndarray[long,ndim=1]particles,
        np.ndarray[double,ndim=1]E,
        np.ndarray[double,ndim=2]_r,
        np.ndarray[double,ndim=1]_q,
        np.ndarray[double,ndim=2]_p0,
        np.ndarray[double,ndim=3]_a0,
        np.ndarray[double,ndim=4]_b0,
        np.ndarray[double,ndim=2]_field,
        int max_it = 100,
        double threshold = 1e-8,
        int num_threads = 1
        ):
    """An optimized version of solve_scf_for_external which explicitly takes
    arrays of the particles properties, and outputs the local field at each pointa
    after the residual is below threshold"""

    cdef int Nmax = particles.shape[0]

    cdef np.ndarray[double, ndim=2] E_p0 = np.zeros( (Nmax, 3))
    cdef np.ndarray[double, ndim=2] E_at_p = np.zeros( (Nmax, 3 ))
    cdef double[:,:] para_field = _field
    E_at_p[:, :] = _field

    cdef int i, o, p, k, j, l
    cdef double residual, dr2, tmp_dr, tmp_x, tmp_y, tmp_z

    cdef double rx, ry, rz
    cdef double px, py, pz

    cdef double ax, ay, az, bx, by, bz

#dipole components for particle o
    cdef double p_o_x, p_o_y, p_o_z

#monopole/dipole x, y, z component from particle o
    cdef double proj_o
    cdef double mx, my, mz
    cdef double dx, dy, dz
    cdef double tmp_E_x, tmp_E_y,tmp_E_z

    for i in range( max_it ):
#Parallelize over outer loop, over each particle p
        for p in prange( Nmax, num_threads = num_threads,
                nogil = True):
            tmp_E_x = 0
            tmp_E_y = 0
            tmp_E_z = 0
            for o in range( Nmax ):
                if particles[p] == particles[o]:
                    continue
                #od = c_od( od, _field, _p0, _a0, _b0 )
                ax = 0
                ay = 0
                az = 0
                bx = 0
                by = 0
                bz = 0
                for k in range(3):
                    ax = ax + _a0[o, 0, k ] * E_at_p[o, k]
                    ay = ay + _a0[o, 1, k ] * E_at_p[o, k]
                    az = az + _a0[o, 2, k ] * E_at_p[o, k]
                    for j in range(3):
                        bx = bx + 0.5*(_b0[o, 0, k, j ] * E_at_p[o, k]* E_at_p[o, j])
                        by = by + 0.5*(_b0[o, 1, k, j ] * E_at_p[o, k]* E_at_p[o, j])
                        bz = bz + 0.5*(_b0[o, 2, k, j ] * E_at_p[o, k]* E_at_p[o, j])
                p_o_x = _p0[o, 0] + ax + bx
                p_o_y = _p0[o, 1] + ay + by
                p_o_z = _p0[o, 2] + az + bz

                #printf( "p at o: %f, %f, %f\n", p_o_x, p_o_y , p_o_z ) 
                # + adot[ :] \
                        #+ 0.5*np.dot( np.dot( _b0[o], _field[o]), _field[o] )
#Calculate distance vectors
                rx = _r[p, 0] - _r[o, 0]
                ry = _r[p, 1] - _r[o, 1]
                rz = _r[p, 2] - _r[o, 2]
#This is the distance using norm using clib.math.sqrt
                dr2 = rx*rx + ry*ry + rz*rz

                mx = _q[o] * rx / pow(dr2, 1.5 )
                my = _q[o] * ry / pow(dr2, 1.5 )
                mz = _q[o] * rz / pow(dr2, 1.5 )

                proj_o = rx*p_o_x + ry*p_o_y + rz*p_o_z

                dx = (3*rx*proj_o - dr2 * p_o_x)/pow( dr2, 2.5 )
                dy = (3*ry*proj_o - dr2 * p_o_y)/pow( dr2, 2.5 )
                dz = (3*rz*proj_o - dr2 * p_o_z)/pow( dr2, 2.5 )

                tmp_E_x = tmp_E_x + mx + dx
                tmp_E_y = tmp_E_y + my + dy
                tmp_E_z = tmp_E_z + mz + dz

            _field[ p, 0] = tmp_E_x + E[0]
            _field[ p, 1] = tmp_E_y + E[1]
            _field[ p, 2] = tmp_E_z + E[2]

        E_at_p[:, :] = _field
        residual = np.linalg.norm( E_p0 - E_at_p)
        #print residual, threshold
        if residual < threshold:
            return E_at_p, i, residual
        E_p0[:, :] = E_at_p
    raise SCFNotConverged(residual, threshold)
