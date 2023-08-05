# -*- coding: utf-8 -*-

"""Copyright 2015 Roger R Labbe Jr.

FilterPy library.
http://github.com/rlabbe/filterpy

Documentation at:
https://filterpy.readthedocs.org

Supporting book at:
https://github.com/rlabbe/Kalman-and-Bayesian-Filters-in-Python

This is licensed under an MIT license. See the readme.MD file
for more information.
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from filterpy.common import setter, setter_1d, setter_scalar, dot3
import numpy as np
from numpy import dot, zeros, eye, isscalar
import scipy.linalg as linalg
from scipy.stats import multivariate_normal


class KalmanFilter(object):
    """ Implements a Kalman filter. You are responsible for setting the
    various state variables to reasonable values; the defaults  will
    not give you a functional filter.

    You will have to set the following attributes after constructing this
    object for the filter to perform properly. Please note that there are
    various checks in place to ensure that you have made everything the
    'correct' size. However, it is possible to provide incorrectly sized
    arrays such that the linear algebra can not perform an operation.
    It can also fail silently - you can end up with matrices of a size that
    allows the linear algebra to work, but are the wrong shape for the problem
    you are trying to solve.

    **Attributes**

    x : numpy.array(dim_x, 1)
        state estimate vector

    P : numpy.array(dim_x, dim_x)
        covariance estimate matrix

    R : numpy.array(dim_z, dim_z)
        measurement noise matrix

    Q : numpy.array(dim_x, dim_x)
        process noise matrix

    F : numpy.array()
        State Transition matrix

    H : numpy.array(dim_x, dim_x)


    You may read the following attributes.

    **Readable Attributes**

    y : numpy.array
        Residual of the update step.

    K : numpy.array(dim_x, dim_z)
        Kalman gain of the update step

    S :  numpy.array
        Systen uncertaintly projected to measurement space

    likelihood : scalar
        Likelihood of last measurment update.

    log_likelihood : scalar
        Log likelihood of last measurment update.


    """



    def __init__(self, dim_x, dim_z, dim_u=0):
        """ Create a Kalman filter. You are responsible for setting the
        various state variables to reasonable values; the defaults below will
        not give you a functional filter.

        **Parameters**

        dim_x : int
            Number of state variables for the Kalman filter. For example, if
            you are tracking the position and velocity of an object in two
            dimensions, dim_x would be 4.

            This is used to set the default size of P, Q, and u

        dim_z : int
            Number of of measurement inputs. For example, if the sensor
            provides you with position in (x,y), dim_z would be 2.

        dim_u : int (optional)
            size of the control input, if it is being used.
            Default value of 0 indicates it is not used.
        """

        assert dim_x > 0
        assert dim_z > 0
        assert dim_u >= 0

        self.dim_x = dim_x
        self.dim_z = dim_z
        self.dim_u = dim_u

        self._x = zeros((dim_x,1)) # state
        self._P = eye(dim_x)       # uncertainty covariance
        self._Q = eye(dim_x)       # process uncertainty
        self._B = 0                # control transition matrix
        self._F = 0                # state transition matrix
        self.H = 0                 # Measurement function
        self.R = eye(dim_z)        # state uncertainty
        self._alpha_sq = 1.        # fading memory control
        self.M = 0                 # process-measurement cross correlation

        # gain and residual are computed during the innovation step. We
        # save them so that in case you want to inspect them for various
        # purposes
        self._K = 0 # kalman gain
        self._y = zeros((dim_z, 1))
        self._S = np.zeros((dim_z, dim_z)) # system uncertainty

        # identity matrix. Do not alter this.
        self._I = np.eye(dim_x)


    def update(self, z, R=None, H=None):
        """
        Add a new measurement (z) to the Kalman filter. If z is None, nothing
        is changed.

        **Parameters**

        z : np.array
            measurement for this update.

        R : np.array, scalar, or None
            Optionally provide R to override the measurement noise for this
            one call, otherwise  self.R will be used.

        H : np.array, or None
            Optionally provide H to override the measurement function for this
            one call, otherwise self.H will be used.

        """

        if z is None:
            return

        if R is None:
            R = self.R
        elif isscalar(R):
            R = eye(self.dim_z) * R

        # rename for readability and a tiny extra bit of speed
        if H is None:
            H = self.H
        P = self._P
        x = self._x

        # y = z - Hx
        # error (residual) between measurement and prediction
        self._y = z - dot(H, x)

        # S = HPH' + R
        # project system uncertainty into measurement space
        S = dot3(H, P, H.T) + R

        mean = np.array(dot(H, x)).flatten()
        flatz = np.array(z).flatten()

        self.likelihood = multivariate_normal.pdf(flatz, mean, cov=S, allow_singular=True)
        self.log_likelihood = multivariate_normal.logpdf(flatz, mean, cov=S, allow_singular=True)

        # K = PH'inv(S)
        # map system uncertainty into kalman gain
        K = dot3(P, H.T, linalg.inv(S))

        # x = x + Ky
        # predict new x with residual scaled by the kalman gain
        self._x = x + dot(K, self._y)

        # P = (I-KH)P(I-KH)' + KRK'
        I_KH = self._I - dot(K, H)
        self._P = dot3(I_KH, P, I_KH.T) + dot3(K, R, K.T)

        self._S = S
        self._K = K



    def update_correlated(self, z, R=None, H=None):
        """ Add a new measurement (z) to the Kalman filter assuming that
        process noise and measurement noise are correlated as defined in
        the `self.M` matrix.

        If z is None, nothing is changed.

        **Parameters**

        z : np.array
            measurement for this update.

        R : np.array, scalar, or None
            Optionally provide R to override the measurement noise for this
            one call, otherwise  self.R will be used.

        H : np.array,  or None
            Optionally provide H to override the measurement function for this
            one call, otherwise  self.H will be used.

        """

        if z is None:
            return

        if R is None:
            R = self.R
        elif isscalar(R):
            R = eye(self.dim_z) * R

        # rename for readability and a tiny extra bit of speed
        if H is None:
            H = self.H
        x = self._x
        P = self._P
        M = self.M

        # y = z - Hx
        # error (residual) between measurement and prediction
        self._y = z - dot(H, x)

        # project system uncertainty into measurement space
        S = dot3(H, P, H.T) + dot(H, M) + dot(M.T, H.T) + R

        mean = np.array(dot(H, x)).flatten()
        flatz = np.array(z).flatten()

        self.likelihood = multivariate_normal.pdf(flatz, mean, cov=S, allow_singular=True)
        self.log_likelihood = multivariate_normal.logpdf(flatz, mean, cov=S, allow_singular=True)

        # K = PH'inv(S)
        # map system uncertainty into kalman gain
        K = dot(dot(P, H.T) + M, linalg.inv(S))

        # x = x + Ky
        # predict new x with residual scaled by the kalman gain
        self._x = x + dot(K, self._y)
        self._P = P - dot(K, dot(H, P) + M.T)

        self._S = S
        self._K = K


    def test_matrix_dimensions(self):
        """ Performs a series of asserts to check that the size of everything
        is what it should be. This can help you debug problems in your design.

        This is only a test; you do not need to use it while filtering.
        However, to use you will want to perform at least one predict() and
        one update() before calling; some bad designs will cause the shapes
        of x and P to change in a silent and bad way. For example, if you
        pass in a badly dimensioned z into update that can cause x to be
        misshapen."""

        assert self._x.shape == (self.dim_x, 1), \
               "Shape of x must be ({},{}), but is {}".format(
               self.dim_x, 1, self._x.shape)

        assert self._P.shape == (self.dim_x, self.dim_x), \
               "Shape of P must be ({},{}), but is {}".format(
               self.dim_x, self.dim_x, self._P.shape)

        assert self._Q.shape == (self.dim_x, self.dim_x), \
               "Shape of P must be ({},{}), but is {}".format(
               self.dim_x, self.dim_x, self._P.shape)


    def predict(self, u=0, B=None, F=None, Q=None):
        """ Predict next position using the Kalman filter state propagation
        equations.

        **Parameters**

        u : np.array
            Optional control vector. If non-zero, it is multiplied by B
            to create the control input into the system.

        B : np.array(dim_x, dim_z), or None
            Optional control transition matrix; a value of None in
            any position will cause the filter to use `self.B`.

        F : np.array(dim_x, dim_x), or None
            Optional state transition matrix; a value of None in
            any position will cause the filter to use `self.F`.

        Q : np.array(dim_x, dim_x), scalar, or None
            Optional process noise matrix; a value of None in
            any position will cause the filter to use `self.Q`.
        """

        if B is None:
            B = self._B
        if F is None:
            F = self._F
        if Q is None:
            Q = self._Q
        elif isscalar(Q):
            Q = eye(self.dim_x) * Q

        # x = Fx + Bu
        self._x = dot(F, self.x) + dot(B, u)

        # P = FPF' + Q
        self._P = self._alpha_sq * dot3(F, self._P, F.T) + Q


    def batch_filter(self, zs, Fs=None, Qs=None, Hs=None, Rs=None, Bs=None, us=None, update_first=False):
        """ Batch processes a sequences of measurements.

        **Parameters**

        zs : list-like
            list of measurements at each time step `self.dt` Missing
            measurements must be represented by 'None'.

        Fs : list-like, optional
            optional list of values to use for the state transition matrix matrix;
            a value of None in any position will cause the filter
            to use `self.F` for that time step.

        Qs : list-like, optional
            optional list of values to use for the process error
            covariance; a value of None in any position will cause the filter
            to use `self.Q` for that time step.

        Hs : list-like, optional
            optional list of values to use for the measurement matrix;
            a value of None in any position will cause the filter
            to use `self.H` for that time step.

        Rs : list-like, optional
            optional list of values to use for the measurement error
            covariance; a value of None in any position will cause the filter
            to use `self.R` for that time step.

        Bs : list-like, optional
            optional list of values to use for the control transition matrix;
            a value of None in any position will cause the filter
            to use `self.B` for that time step.

        us : list-like, optional
            optional list of values to use for the control input vector;
            a value of None in any position will cause the filter to use
            0 for that time step.

        update_first : bool, optional,
            controls whether the order of operations is update followed by
            predict, or predict followed by update. Default is predict->update.

        **Returns**

        means: np.array((n,dim_x,1))
            array of the state for each time step after the update. Each entry
            is an np.array. In other words `means[k,:]` is the state at step
            `k`.

        covariance: np.array((n,dim_x,dim_x))
            array of the covariances for each time step after the update.
            In other words `covariance[k,:,:]` is the covariance at step `k`.

        means_predictions: np.array((n,dim_x,1))
            array of the state for each time step after the predictions. Each
            entry is an np.array. In other words `means[k,:]` is the state at
            step `k`.

        covariance_predictions: np.array((n,dim_x,dim_x))
            array of the covariances for each time step after the prediction.
            In other words `covariance[k,:,:]` is the covariance at step `k`.

        **Example**

        zs = [t + random.randn()*4 for t in range (40)]
        Fs = [kf.F for t in range (40)]
        Hs = [kf.H for t in range (40)]

        (mu, cov, _, _) = kf.batch_filter(zs, Rs=R_list, Fs=Fs, Hs=Hs, Qs=None,
                                          Bs=None, us=None, update_first=False)
        (xs, Ps, Ks) = kf.rts_smoother(mu, cov, Fs=Fs, Qs=None)

        """

        n = np.size(zs,0)
        if Fs is None:
            Fs = [self.F] * n
        if Qs is None:
            Qs = [self.Q] * n
        if Hs is None:
            Hs = [self.H] * n
        if Rs is None:
            Rs = [self.R] * n
        if Bs is None:
            Bs = [self.B] * n
        if us is None:
            us = [0] * n

        # mean estimates from Kalman Filter
        if self.x.ndim == 1:
            means   = zeros((n, self.dim_x))
            means_p = zeros((n, self.dim_x))
        else:
            means   = zeros((n, self.dim_x, 1))
            means_p = zeros((n, self.dim_x, 1))

        # state covariances from Kalman Filter
        covariances   = zeros((n, self.dim_x, self.dim_x))
        covariances_p = zeros((n, self.dim_x, self.dim_x))

        if update_first:
            for i, (z, F, Q, H, R, B, u) in enumerate(zip(zs, Fs, Qs, Hs, Rs, Bs, us)):

                self.update(z, R=R, H=H)
                means[i,:]         = self._x
                covariances[i,:,:] = self._P

                self.predict(u=u, B=B, F=F, Q=Q)
                means_p[i,:]         = self._x
                covariances_p[i,:,:] = self._P
        else:
            for i, (z, F, Q, H, R, B, u) in enumerate(zip(zs, Fs, Qs, Hs, Rs, Bs, us)):

                self.predict(u=u, B=B, F=F, Q=Q)
                means_p[i,:]         = self._x
                covariances_p[i,:,:] = self._P

                self.update(z, R=R, H=H)
                means[i,:]         = self._x
                covariances[i,:,:] = self._P

        return (means, covariances, means_p, covariances_p)



    def rts_smoother(self, Xs, Ps, Fs=None, Qs=None):
        """ Runs the Rauch-Tung-Striebal Kalman smoother on a set of
        means and covariances computed by a Kalman filter. The usual input
        would come from the output of `KalmanFilter.batch_filter()`.

        **Parameters**

        Xs : numpy.array
           array of the means (state variable x) of the output of a Kalman
           filter.

        Ps : numpy.array
            array of the covariances of the output of a kalman filter.

        Fs : list-like collection of numpy.array, optional
            State transition matrix of the Kalman filter at each time step. 
            Optional, if not provided the filter's self.F will be used

        Qs : list-like collection of numpy.array, optional
            Process noise of the Kalman filter at each time step. Optional,
            if not provided the filter's self.Q will be used

        **Returns**

        'x' : numpy.ndarray
           smoothed means

        'P' : numpy.ndarray
           smoothed state covariances

        'K' : numpy.ndarray
            smoother gain at each step


        **Example**::

            zs = [t + random.randn()*4 for t in range (40)]

            (mu, cov, _, _) = kalman.batch_filter(zs)
            (x, P, K) = rts_smoother(mu, cov, kf.F, kf.Q)

        """

        assert len(Xs) == len(Ps)
        shape = Xs.shape
        n = shape[0]
        dim_x = shape[1]

        if Fs is None:
            Fs = [self.F] * n
        if Qs is None:
            Qs = [self.Q] * n

        # smoother gain
        K = zeros((n,dim_x,dim_x))

        x, P = Xs.copy(), Ps.copy()

        for k in range(n-2,-1,-1):
            P_pred = dot3(Fs[k], P[k], Fs[k].T) + Qs[k]

            K[k]  = dot3(P[k], Fs[k].T, linalg.inv(P_pred))
            x[k] += dot (K[k], x[k+1] - dot(Fs[k], x[k]))
            P[k] += dot3 (K[k], P[k+1] - P_pred, K[k].T)

        return (x, P, K)


    def get_prediction(self, u=0):
        """ Predicts the next state of the filter and returns it. Does not
        alter the state of the filter.

        **Parameters**

        u : np.array
            optional control input

        **Returns**

        (x, P)
            State vector and covariance array of the prediction.
        """

        x = dot(self._F, self._x) + dot(self._B, u)
        P = self._alpha_sq * dot3(self._F, self._P, self._F.T) + self._Q
        return (x, P)


    def residual_of(self, z):
        """ returns the residual for the given measurement (z). Does not alter
        the state of the filter.
        """
        return z - dot(self.H, self._x)


    def measurement_of_state(self, x):
        """ Helper function that converts a state into a measurement.

        **Parameters**

        x : np.array
            kalman state vector

        **Returns**

        z : np.array
            measurement corresponding to the given state
        """

        return dot(self.H, x)


    @property
    def alpha(self):
        """ Fading memory setting. 1.0 gives the normal Kalman filter, and
        values slightly larger than 1.0 (such as 1.02) give a fading
        memory effect - previous measurements have less influence on the
        filter's estimates. This formulation of the Fading memory filter
        (there are many) is due to Dan Simon [1].

        ** References **

        [1] Dan Simon. "Optimal State Estimation." John Wiley & Sons.
            p. 208-212. (2006)
        """

        return self._alpha_sq**.5


    @alpha.setter
    def alpha(self, value):
        assert np.isscalar(value)
        assert value > 0

        self._alpha_sq = value**2

    @property
    def Q(self):
        """ Process uncertainty"""
        return self._Q


    @Q.setter
    def Q(self, value):
        self._Q = setter_scalar(value, self.dim_x)

    @property
    def P(self):
        """ covariance matrix"""
        return self._P


    @P.setter
    def P(self, value):
        self._P = setter_scalar(value, self.dim_x)


    @property
    def F(self):
        """ state transition matrix"""
        return self._F


    @F.setter
    def F(self, value):
        self._F = setter(value, self.dim_x, self.dim_x)

    @property
    def B(self):
        """ control transition matrix"""
        return self._B


    @B.setter
    def B(self, value):
        self._B = value
        """ control transition matrix"""
        if np.isscalar(value):
            self._B = value
        else:
            self._B = setter (value, self.dim_x, self.dim_u)


    @property
    def x(self):
        """ filter state vector."""
        return self._x


    @x.setter
    def x(self, value):
        self._x = setter_1d(value, self.dim_x)


    @property
    def K(self):
        """ Kalman gain """
        return self._K


    @property
    def y(self):
        """ measurement residual (innovation) """
        return self._y

    @property
    def S(self):
        """ system uncertainty in measurement space """
        return self._S
