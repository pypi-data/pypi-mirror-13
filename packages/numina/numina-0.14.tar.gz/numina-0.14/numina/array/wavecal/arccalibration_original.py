from __future__ import division
from __future__ import print_function

try:
    import matplotlib.pyplot as plt
    HAVE_PLOTS = True
except ImportError:
    HAVE_PLOTS = False
import numpy as np
from numpy.polynomial import polynomial
import itertools
import scipy.misc

from ..robustfit import fit_theil_sen
from .statsummary import sigmaG
# -----------------------------------------------------------------------------

def select_data_for_fit(wv_master, xpos_arc, solution):
    """Select information from valid arc lines to facilitate posterior fits.

    Parameters
    ----------
    wv_master : 1d numpy array, float
        Array with wavelengths corresponding to the master table (Angstroms).
    xpos_arc : 1d numpy array, float
        Location of arc lines (pixels).
    solution : ouput from previous call to arccalibration

    Returns
    -------
    nfit : int
        Number of valid points for posterior fits.
    ifit : list of int
        List of indices corresponding to the arc lines which coordinates are
        going to be employed in the posterior fits.
    xfit : 1d numpy aray
        X coordinate of points for posterior fits.
    yfit : 1d numpy array
        Y coordinate of points for posterior fits.
    wfit : 1d numpy array
        Cost function of points for posterior fits. The inverse of these values
        can be employed for weighted fits.
    """

    nlines_arc = len(solution)

    if nlines_arc != xpos_arc.size:
        raise ValueError('invalid nlines_arc=' + str(nlines_arc))

    nfit = 0
    ifit = []
    xfit = []
    yfit = []
    wfit = []
    for i in range(nlines_arc):
        if solution[i]['lineok']:
            ifit.append(i)
            xfit.append(xpos_arc[i])
            yfit.append(wv_master[solution[i]['id']])
            wfit.append(solution[i]['funcost'])
            nfit += 1
    return nfit, np.array(ifit), np.array(xfit), np.array(yfit), np.array(wfit)


# -----------------------------------------------------------------------------


def fit_solution(wv_master, xpos_arc, solution, poly_degree_wfit, weighted):
    """Fit polynomial to arc calibration solution.

    Parameters
    ----------
    wv_master : 1d numpy array, float
        Array with wavelengths corresponding to the master table (Angstroms).
    xpos_arc : 1d numpy array, float
        Location of arc lines (pixels).
    solution : list of dictionaries
        A list of size equal to the number of arc lines, which elements are
        dictionaries containing all the relevant information concerning the
        line identification.
    naxis1_arc : int
        NAXIS1 of arc spectrum.
    poly_degree_wfit : int
        Polynomial degree corresponding to the wavelength calibration function
        to be fitted.
    weighted : bool
        Determines whether the polynomial fit is weighted or not, using as
        weights the values of the cost function obtained in the line
        identification.
    ldebug : bool
        If True intermediate results are displayed.
    lplot : bool
        If True intermediate plots are displayed.
    lpause: bool
        If True introduce pause.

    Returns
    -------
    coeff : 1d numpy array, float
        Coefficients of the polynomial fit
    crval1_approx : float
        Approximate CRVAL1 value.
    cdetl1_approx : float
        Approximate CDELT1 value.
    """

    nlines_arc = len(solution)

    if nlines_arc != xpos_arc.size:
        raise ValueError('Invalid nlines_arc=' + str(nlines_arc))

    # Select information from valid lines.
    nfit, ifit, xfit, yfit, wfit = select_data_for_fit(wv_master, xpos_arc,
                                                       solution)

    # Select list of filtered out and unidentified lines
    list_R = []
    list_T = []
    list_P = []
    list_unidentified = []
    for i in range(nlines_arc):
        if not solution[i]['lineok']:
            if solution[i]['type'] is None:
                list_unidentified.append(i)
            elif solution[i]['type'] == 'R':
                list_R.append(i)
            elif solution[i]['type'] == 'T':
                list_T.append(i)
            elif solution[i]['type'] == 'P':
                list_P.append(i)
            else:
                raise ValueError('Unexpected "type"')

    # Obtain approximate linear fit using the robust Theil-Sen method.
    intercept, slope = fit_theil_sen(xfit, yfit)

    cdelt1_approx = slope
    crval1_approx = intercept + cdelt1_approx

    # Polynomial fit.
    if weighted:
        coeff = polynomial.polyfit(xfit, yfit, poly_degree_wfit, w=1/wfit)
    else:
        coeff = polynomial.polyfit(xfit, yfit, poly_degree_wfit)

    return coeff, crval1_approx, cdelt1_approx

# -----------------------------------------------------------------------------


def gen_triplets_master(wv_master):
    """Compute information associated to triplets in master table.

    Determine all the possible triplets that can be generated from the
    array `wv_master`. In addition, the relative position of the central
    line of each triplet is also computed.

    Parameters
    ----------
    wv_master : 1d numpy array, float
        Array with wavelengths corresponding to the master table (Angstroms).
    ldebug : bool
        If True intermediate results are displayed.
    lplot : bool
        If True intermediate plots are displayed.

    Returns
    -------
    ntriplets_master : int
        Number of triplets built from master table.
    ratios_master_sorted : 1d numpy array, float
        Array with values of the relative position of the central line of each
        triplet, sorted in ascending order.
    triplets_master_sorted_list : list of tuples
        List with tuples of three numbers, corresponding to the three line
        indices in the master table. The list is sorted to be in correspondence
        with `ratios_master_sorted`.
       
    """

    nlines_master = wv_master.size

    #---
    # Generate all the possible triplets with the numbers of the lines in the
    # master table. Each triplet is defined as a tuple of three numbers
    # corresponding to the three line indices in the master table. The
    # collection of tuples is stored in an ordinary python list.
    iter_comb_triplets = itertools.combinations(range(nlines_master), 3)
    triplets_master_list = [val for val in iter_comb_triplets]

    # Verify that the number of triplets coincides with the expected value.
    ntriplets_master = len(triplets_master_list)
    if ntriplets_master != scipy.misc.comb(nlines_master, 3, exact=True):
        raise ValueError('Invalid number of combinations')

    # For each triplet, compute the relative position of the central line.
    ratios_master = np.zeros(ntriplets_master)

    for index, value in enumerate(triplets_master_list):
        i1, i2, i3 = value
        ratios_master[index] = (wv_master[i2]-wv_master[i1])/(wv_master[i3]-wv_master[i1])

    # Compute the array of indices that index the above ratios in sorted order.
    isort_ratios_master = np.argsort(ratios_master)

    # Simultaneous sort of position ratios and triplets.
    ratios_master_sorted = ratios_master[isort_ratios_master]
    triplets_master_sorted_list = [triplets_master_list[i] for i in isort_ratios_master]

    return ntriplets_master, ratios_master_sorted, triplets_master_sorted_list

# -----------------------------------------------------------------------------


def arccalibration(wv_master, xpos_arc, naxis1_arc, wv_ini_search,
                   wv_end_search, error_xpos_arc, times_sigma_r,
                   frac_triplets_for_sum, times_sigma_theil_sen,
                   poly_degree_wfit, times_sigma_polfilt,times_sigma_inclusion,
                   ldebug=False, lplot=False, lpause=False):
    """Performs line identification for arc calibration.

    This function is a wrapper of two functions, which are responsible of 
    computing all the relevant information concerning the triplets 
    generated from the master table and the actual identification procedure
    of the arc lines, respectively. The separation of those computations in two
    different functions helps to avoid the repetition of calls to the first
    function when calibrating several arcs using the same master table. 

    Parameters
    ----------
    wv_master : 1d numpy array, float
        Array with wavelengths corresponding to the master table (Angstroms).
    xpos_arc : 1d numpy array, float
        Location of arc lines (pixels).
    naxis1_arc : int
        NAXIS1 for arc spectrum.
    wv_ini_search : float
        Minimum valid wavelength.
    wv_end_search : float
        Maximum valid wavelength.
    error_xpos_arc : float
        Error in arc line position (pixels).
    times_sigma_r : float
        Times sigma to search for valid line position ratios.
    frac_triplets_for_sum : float
        Fraction of distances to different triplets to sum when computing the
        cost function.
    times_sigma_theil_sen : float
        Number of times the (robust) standard deviation around the linear fit
        (using the Theil-Sen method) to reject points.
    poly_degree_wfit : int
        Degree for polynomial fit to wavelength calibration.
    times_sigma_polfilt : float
        Number of times the (robust) standard deviation around the polynomial
        fit to reject points.
    times_sigma_inclusion : float
        Number of times the (robust) standard deviation around the polynomial
        fit to include a new line in the set of identified lines.
    ldebug : bool
        If True intermediate results are displayed.
    lplot : bool
        If True intermediate plots are displayed.
    lpause: bool
        If True introduce pause


    Returns
    -------
    solution : list of dictionaries
        A list of size equal to the number of arc lines, which elements are
        dictionaries containing all the relevant information concerning the
        line identification.

    """

    result = gen_triplets_master(wv_master)
    ntriplets_master = result[0]
    ratios_master_sorted = result[1]
    triplets_master_sorted_list = result[2]

    solution = arccalibration_direct(wv_master, ntriplets_master,
                                     ratios_master_sorted,
                                     triplets_master_sorted_list,
                                     xpos_arc, naxis1_arc, wv_ini_search,
                                     wv_end_search, error_xpos_arc,
                                     times_sigma_r, frac_triplets_for_sum,
                                     times_sigma_theil_sen, poly_degree_wfit,
                                     times_sigma_polfilt,times_sigma_inclusion,
                                     ldebug, lplot, lpause)
    return solution

# -----------------------------------------------------------------------------


def arccalibration_direct(wv_master,ntriplets_master,ratios_master_sorted,
                          triplets_master_sorted_list,xpos_arc,naxis1_arc,
                          wv_ini_search, wv_end_search,error_xpos_arc,
                          times_sigma_r,frac_triplets_for_sum,
                          times_sigma_theil_sen, poly_degree_wfit,
                          times_sigma_polfilt, times_sigma_inclusion,
                          ldebug=False, lplot=False, lpause=False):
    """Performs line identification for arc calibration using line triplets.

    This function assumes that a previous call to the function responsible for
    the computation of information related to the triplets derived from the
    master table has been previously executed.

    Parameters
    ----------
    wv_master : 1d numpy array, float
        Array with wavelengths corresponding to the master table (Angstroms).
    ntriplets_master : int
        Number of triplets built from master table.
    ratios_master_sorted : 1d numpy array, float
        Array with values of the relative position of the central line of each
        triplet, sorted in ascending order.
    triplets_master_sorted_list : list of tuples
        List with tuples of three numbers, corresponding to the three line
        indices in the master table. The list is sorted to be in correspondence
        with `ratios_master_sorted`.
    xpos_arc : 1d numpy array, float
        Location of arc lines (pixels).
    naxis1_arc : int
        NAXIS1 for arc spectrum.
    wv_ini_search : float
        Minimum valid wavelength.
    wv_end_search : float
        Maximum valid wavelength.
    error_xpos_arc : float
        Error in arc line position (pixels).
    times_sigma_r : float
        Times sigma to search for valid line position ratios.
    frac_triplets_for_sum : float
        Fraction of distances to different triplets to sum when computing the
        cost function.
    times_sigma_theil_sen : float
        Number of times the (robust) standard deviation around the linear fit
        (using the Theil-Sen method) to reject points.
    poly_degree_wfit : int
        Degree for polynomial fit to wavelength calibration.
    times_sigma_polfilt : float
        Number of times the (robust) standard deviation around the polynomial
        fit to reject points.
    times_sigma_inclusion : float
        Number of times the (robust) standard deviation around the polynomial
        fit to include a new line in the set of identified lines.
    ldebug : bool
        If True intermediate results are displayed.
    lplot : bool
        If True intermediate plots are displayed.


    Returns
    -------
    solution : list of dictionaries
        A list of size equal to the number of arc lines, which elements are
        dictionaries containing all the relevant information concerning the
        line identification.

    """

    nlines_master = wv_master.size

    if wv_ini_search == None:
        wv_ini_search = wv_master.min()
    if wv_end_search == None:
        wv_end_search = wv_master.max()

    nlines_arc = xpos_arc.size
    if nlines_arc < 5:
        raise ValueError('Insufficient arc lines=' + str(nlines_arc))

    # ---
    # Generate triplets with consecutive arc lines. For each triplet,
    # compatible triplets from the master table are sought. Each compatible
    # triplet from the master table provides an estimate for CRVAL1 and CDELT1.
    # As an additional constraint, the only valid solutions are those for which
    # the initial and the final wavelengths for the arc are restricted to a
    # predefined wavelength interval.
    crval1_search = np.array([])
    cdelt1_search = np.array([])
    error_crval1_search = np.array([])
    error_cdelt1_search = np.array([])
    itriplet_search = np.array([])
    clabel_search = []

    ntriplets_arc = nlines_arc - 2
    if ldebug:
        print('>>> Total number of arc lines............:', nlines_arc)
        print('>>> Total number of arc triplets.........:', ntriplets_arc)

    # Loop in all the arc line triplets. Note that only triplets built from
    # consecutive arc lines are considered.
    for i in range(ntriplets_arc):
        i1, i2, i3 = i, i+1, i+2

        dist12 = xpos_arc[i2]-xpos_arc[i1]
        dist13 = xpos_arc[i3]-xpos_arc[i1]
        ratio_arc = dist12/dist13

        pol_r = ratio_arc*(ratio_arc-1)+1
        error_ratio_arc = np.sqrt(2)*error_xpos_arc/dist13*np.sqrt(pol_r)

        ratio_arc_min = max(0.0, ratio_arc-times_sigma_r*error_ratio_arc)
        ratio_arc_max = min(1.0, ratio_arc+times_sigma_r*error_ratio_arc)

        # determine compatible triplets from the master list
        j_loc_min = np.searchsorted(ratios_master_sorted, ratio_arc_min)-1
        j_loc_max = np.searchsorted(ratios_master_sorted, ratio_arc_max)+1

        if j_loc_min < 0:
            j_loc_min = 0
        if j_loc_max > ntriplets_master:
            j_loc_max = ntriplets_master

        if ldebug:
            print(i, ratio_arc_min, ratio_arc, ratio_arc_max,
                  j_loc_min, j_loc_max)

        # each triplet from the master list provides a potential solution
        # for CRVAL1 and CDELT1
        for j_loc in range(j_loc_min, j_loc_max+1):
            j1, j2, j3 = triplets_master_sorted_list[j_loc]
            # initial solutions for CDELT1, CRVAL1 and CRVALN
            cdelt1_temp = (wv_master[j3]-wv_master[j1])/dist13
            crval1_temp = wv_master[j2]-(xpos_arc[i2]-1)*cdelt1_temp
            crvaln_temp = crval1_temp + float(naxis1_arc-1)*cdelt1_temp
            # check that CRVAL1 and CRVALN are within the valid limits
            if wv_ini_search <= crval1_temp <= wv_end_search:
                if wv_ini_search <= crvaln_temp <= wv_end_search:
                    # Compute errors
                    error_crval1_temp = cdelt1_temp*error_xpos_arc* \
                      np.sqrt(1+2*((xpos_arc[i2]-1)**2)/(dist13**2))
                    error_cdelt1_temp = np.sqrt(2)*cdelt1_temp* \
                      error_xpos_arc/dist13
                    # Store values and errors
                    crval1_search = np.append(crval1_search, crval1_temp)
                    cdelt1_search = np.append(cdelt1_search, cdelt1_temp)
                    error_crval1_search = np.append(error_crval1_search,
                                                    error_crval1_temp)
                    error_cdelt1_search = np.append(error_cdelt1_search,
                                                    error_cdelt1_temp)
                    # Store additional information about the triplets
                    itriplet_search = np.append(itriplet_search, i)
                    clabel_search.append((j1, j2, j3))

    # Maximum allowed value for CDELT1
    cdelt1_max = (wv_end_search-wv_ini_search)/float(naxis1_arc-1)

    if lplot and HAVE_PLOTS:
        # CDELT1 vs CRVAL1 diagram (original coordinates)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('cdelt1 (Angstroms/pixel)')
        ax.set_ylabel('crval1 (Angstroms)')
        ax.scatter(cdelt1_search, crval1_search, s=200, alpha=0.1)
        xmin = 0.0
        xmax = cdelt1_max
        dx = xmax-xmin
        xmin -= dx/20
        xmax += dx/20
        ax.set_xlim([xmin,xmax])
        ymin = wv_ini_search
        ymax = wv_end_search
        dy = ymax-ymin
        ymin -= dy/20
        ymax += dy/20
        ax.set_ylim([ymin,ymax])
        xp_limits = np.array([0., cdelt1_max])
        yp_limits = wv_end_search-float(naxis1_arc-1)*xp_limits
        xp_limits = np.concatenate((xp_limits,[xp_limits[0],xp_limits[0]]))
        yp_limits = np.concatenate((yp_limits,[yp_limits[1],yp_limits[0]]))
        ax.plot(xp_limits, yp_limits, linestyle='-', color='red')
        plt.show(block=False)
        print('Number of points in last plot:', len(cdelt1_search))
        if lpause:
            raw_input('press <RETURN> to continue...')

    # Normalize the values of CDELT1 and CRVAL1 to the interval [0,1] in each
    # case.
    cdelt1_search_norm = cdelt1_search/cdelt1_max
    error_cdelt1_search_norm = error_cdelt1_search/cdelt1_max
    #
    crval1_search_norm = (crval1_search-wv_ini_search)
    crval1_search_norm /= (wv_end_search-wv_ini_search)
    error_crval1_search_norm = error_crval1_search/(wv_ini_search-wv_end_search)

    # Intermediate plots
    if lplot and HAVE_PLOTS:
        # CDELT1 vs CRVAL1 diagram (original coordinates)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('cdelt1 (Angstroms/pixel)')
        ax.set_ylabel('crval1 (Angstroms)')
        ax.scatter(cdelt1_search, crval1_search, s=200, alpha=0.1)
        xmin = 0.0
        xmax = cdelt1_max
        dx = xmax-xmin
        xmin -= dx/20
        xmax += dx/20
        ax.set_xlim([xmin,xmax])
        ymin = wv_ini_search
        ymax = wv_end_search
        dy = ymax-ymin
        ymin -= dy/20
        ymax += dy/20
        ax.set_ylim([ymin,ymax])
        xp_limits = np.array([0., cdelt1_max])
        yp_limits = wv_end_search-float(naxis1_arc-1)*xp_limits
        xp_limits = np.concatenate((xp_limits,[xp_limits[0],xp_limits[0]]))
        yp_limits = np.concatenate((yp_limits,[yp_limits[1],yp_limits[0]]))
        ax.plot(xp_limits, yp_limits, linestyle='-', color='red')
        plt.show(block=False)
        print('Number of points in last plot:', len(cdelt1_search))
        if lpause:
            raw_input('press <RETURN> to continue...')

        # CDELT1 vs CRVAL1 diagram (normalized coordinates)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('normalized cdelt1')
        ax.set_ylabel('normalized crval1')
        ax.scatter(cdelt1_search_norm, crval1_search_norm, s=200, alpha=0.1)
        xmin = -0.05
        xmax =  1.05
        ymin = -0.05
        ymax =  1.05
        ax.set_xlim([xmin,xmax])
        ax.set_ylim([ymin,ymax])
        xp_limits = np.array([0.,1.,0.,0.])
        yp_limits = np.array([1.,0.,0.,1.])
        ax.plot(xp_limits, yp_limits, linestyle='-', color='red')
        plt.show(block=False)
        print('Number of points in last plot:', len(cdelt1_search))
        if lpause:
            raw_input('press <RETURN> to continue...')

        # CDELT1 vs CRVAL1 diagram (normalized coordinates)
        # with different color for each arc triplet and overplotting 
        # the arc triplet number
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('normalized cdelt1')
        ax.set_ylabel('normalized crval1')
        ax.scatter(cdelt1_search_norm, crval1_search_norm, s=200, alpha=0.1,
                   c=itriplet_search)
        for i in range(len(itriplet_search)):
            ax.text(cdelt1_search_norm[i], crval1_search_norm[i], 
                    str(int(itriplet_search[i])), fontsize=6)
        ax.set_xlim([xmin,xmax])
        ax.set_ylim([ymin,ymax])
        ax.plot(xp_limits, yp_limits, linestyle='-', color='red')
        plt.show(block=False)
        if lpause:
            raw_input('press <RETURN> to continue...')

        # CDELT1 vs CRVAL1 diagram (normalized coordinates)
        # including triplet numbers
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('normalized cdelt1')
        ax.set_ylabel('normalized crval1')
        ax.scatter(cdelt1_search_norm, crval1_search_norm, s=200, alpha=0.1,
                   c=itriplet_search)
        for i in range(len(clabel_search)):
            ax.text(cdelt1_search_norm[i], crval1_search_norm[i], 
                    clabel_search[i], fontsize=6)
        ax.set_xlim([xmin,xmax])
        ax.set_ylim([ymin,ymax])
        ax.plot(xp_limits, yp_limits, linestyle='-', color='red')
        plt.show(block=False)
        if lpause:
            raw_input('press <RETURN> to continue...')

        # CDELT1 vs CRVAL1 diagram (normalized coordinates)
        # with error bars (note that errors in this plot are highly
        # correlated)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('normalized cdelt1')
        ax.set_ylabel('normalized crval1')
        ax.errorbar(cdelt1_search_norm, crval1_search_norm, 
                    xerr=error_cdelt1_search_norm,
                    yerr=error_crval1_search_norm,
                    fmt='none')
        ax.set_xlim([xmin,xmax])
        ax.set_ylim([ymin,ymax])
        ax.plot(xp_limits, yp_limits, linestyle='-', color='red')
        plt.show(block=False)
        if lpause:
            raw_input('press <RETURN> to continue...')


    # ---
    # Segregate the different solutions (normalized to [0,1]) by triplet. In
    # this way the solutions are saved in different layers (a layer for each
    # triplet). The solutions will be stored as python lists of numpy arrays.
    ntriplets_layered_list = []
    cdelt1_layered_list = []
    error_cdelt1_layered_list = []
    crval1_layered_list = []
    error_crval1_layered_list = []
    itriplet_layered_list = []
    clabel_layered_list = []
    for i in range(ntriplets_arc):
        ldum = (itriplet_search == i)
        ntriplets_layered_list.append(ldum.sum())
        #
        cdelt1_dum = cdelt1_search_norm[ldum]
        cdelt1_layered_list.append(cdelt1_dum)
        error_cdelt1_dum = error_cdelt1_search_norm[ldum]
        error_cdelt1_layered_list.append(error_cdelt1_dum)
        #
        crval1_dum = crval1_search_norm[ldum]
        crval1_layered_list.append(crval1_dum)
        error_crval1_dum = error_crval1_search_norm[ldum]
        error_crval1_layered_list.append(error_crval1_dum)
        #
        itriplet_dum = itriplet_search[ldum]
        itriplet_layered_list.append(itriplet_dum)
        #
        clabel_dum = [k for (k, v) in zip(clabel_search, ldum) if v]
        clabel_layered_list.append(clabel_dum)
    
    if ldebug:
        print('>>> List with no. of solutions/triplet...:',
              ntriplets_layered_list)
        print('>>> Total number of potential solutions..:',
              sum(ntriplets_layered_list))
        if lpause:
            raw_input('press <RETURN> to continue...')

    # ---
    # Computation of the cost function.
    #
    # For each solution, corresponding to a particular triplet, find the
    # nearest solution in each of the remaining ntriplets_arc-1 layers.
    # Compute the distance (in normalized coordinates) to those closest
    # solutions, and obtain the sum of distances considering only a fraction
    # of them (after sorting them in ascending order).
    #
    # Note: in the next instruction the int(???+0.5) function is used
    # instead of round() because different results are obtained when
    # using python 2.7 vs. 3.4
    ntriplets_for_sum = \
      max(1, int(frac_triplets_for_sum*float(ntriplets_arc)+0.5))
    funcost_search = np.zeros(len(itriplet_search))
    for k in range(len(itriplet_search)):
        itriplet_local = itriplet_search[k]
        x0 = cdelt1_search_norm[k]
        y0 = crval1_search_norm[k]
        dist_to_layers = np.array([])
        for i in range(ntriplets_arc):
            if i != itriplet_local:
                if ntriplets_layered_list[i] > 0:
                    x1 = cdelt1_layered_list[i]
                    y1 = crval1_layered_list[i]
                    dist2 = (x0-x1)**2 + (y0-y1)**2
                    dist_to_layers = np.append(dist_to_layers, dist2.min())
                else:
                    dist_to_layers = np.append(dist_to_layers, np.inf)
        dist_to_layers.sort() # in-place sort
        funcost_search[k] = dist_to_layers[range(ntriplets_for_sum)].sum()

    # Normalize the cost function
    funcost_min = funcost_search.min()
    if ldebug:
        print('funcost_min:',funcost_min)
    funcost_search /= funcost_min

    # Segregate the cost function by arc triplet.
    funcost_layered_list = []
    for i in range(ntriplets_arc):
        ldum = (itriplet_search == i)
        funcost_dum = funcost_search[ldum]
        funcost_layered_list.append(funcost_dum)
    if ldebug:
        for i in range(ntriplets_arc):
            jdum = funcost_layered_list[i].argmin()
            print('>>>',i,funcost_layered_list[i][jdum],
                  clabel_layered_list[i][jdum],
                  cdelt1_layered_list[i][jdum], 
                  crval1_layered_list[i][jdum])
        if lpause:
            raw_input('press <RETURN> to continue...')

    # Intermediate plots
    if lplot and HAVE_PLOTS:
        # CDELT1 vs CRVAL1 diagram (normalized coordinates)
        # with symbol size proportional to the inverse of the cost function
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('normalized cdelt1')
        ax.set_ylabel('normalized crval1')
        ax.scatter(cdelt1_search_norm, crval1_search_norm, 
                   s=2000/funcost_search, c=itriplet_search, alpha=0.2)
        ax.set_xlim([xmin,xmax])
        ax.set_ylim([ymin,ymax])
        ax.plot(xp_limits, yp_limits, linestyle='-', color='red')
        plt.show(block=False)
        print('Number of points in last plot:', len(cdelt1_search))
        if lpause:
            raw_input('press <RETURN> to continue...')

        # CDELT1 vs CRVAL1 diagram (normalized coordinates)
        # with symbol size proportional to the inverse of the cost function
        # and over-plotting triplet number
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set_xlabel('normalized cdelt1')
        ax.set_ylabel('normalized crval1')
        ax.scatter(cdelt1_search_norm, crval1_search_norm, 
                   s=2000/funcost_search, c=itriplet_search, alpha=0.2)
        for i in range(len(itriplet_search)):
            ax.text(cdelt1_search_norm[i], crval1_search_norm[i], 
                    str(int(itriplet_search[i])), fontsize=6)
        ax.set_xlim([xmin,xmax])
        ax.set_ylim([ymin,ymax])
        ax.plot(xp_limits, yp_limits, linestyle='-', color='red')
        plt.show(block=False)
        print('Number of points in last plot:', len(cdelt1_search))
        if lpause:
            raw_input('press <RETURN> to continue...')

        # CDELT1 vs CRVAL1 diagram (normalized coordinates)
        for i in range(ntriplets_arc):
            fig = plt.figure()
            ax = fig.add_subplot(111)
            ax.set_xlabel('normalized cdelt1')
            ax.set_ylabel('normalized crval1')
            xdum = cdelt1_layered_list[i]
            ydum = crval1_layered_list[i]
            sdum = 2000/funcost_layered_list[i]
            ax.scatter(xdum, ydum, s=sdum, alpha=0.8)
            ax.set_xlim([xmin,xmax])
            ax.set_ylim([ymin,ymax])
            ax.set_title('Arc triplet number '+str(i))
            ax.plot(xp_limits, yp_limits, linestyle='-', color='red')
            plt.show(block=False)
            print('Number of points in last plot:', xdum.size)
            if lpause:
                raw_input('press <RETURN> to continue...')

    # ---
    # Line identification: several scenarios are considered.
    #
    # * Lines with three identifications:
    #   - Type A: the three identifications are identical. Keep the lowest
    #     value of the three cost functions.
    #   - Type B: two identifications are identical and one is different. Keep
    #     the line with two identifications and the lowest of the corresponding
    #     two cost functions.
    #   - Type C: the three identifications are different. Keep the one which
    #     is closest to a previously identified type B line. Use the
    #     corresponding cost function.
    #
    # * Lines with two identifications (second and penultimate lines).
    #   - Type D: the two identifications are identical. Keep the lowest cost
    #     function value.
    #
    # * Lines with only one identification (first and last lines).
    #   - Type E: the two lines next (or previous) to the considered line have
    #     been identified. Keep its cost function.
    #

    # We store the identifications of each line in a python list of lists
    # named diagonal_ids (which grows as the different triplets are
    # considered). A similar list of lists is also employed to store the
    # corresponding cost functions.
    for i in range(ntriplets_arc):
        jdum = funcost_layered_list[i].argmin()
        k1, k2, k3 = clabel_layered_list[i][jdum]
        funcost_dum = funcost_layered_list[i][jdum]
        if i == 0:
            diagonal_ids = [[k1],[k2],[k3]]
            diagonal_funcost = [[funcost_dum],[funcost_dum], [funcost_dum]]
        else:
            diagonal_ids[i].append(k1)
            diagonal_ids[i+1].append(k2)
            diagonal_ids.append([k3])
            diagonal_funcost[i].append(funcost_dum)
            diagonal_funcost[i+1].append(funcost_dum)
            diagonal_funcost.append([funcost_dum])
    
    if ldebug:
        for i in range(nlines_arc):
            print(i, diagonal_ids[i],diagonal_funcost[i])
        if lpause:
            raw_input('press <RETURN> to continue...')

    # The solutions are stored in a list of dictionaries. The dictionaries
    # contain the following elements:
    # - lineok: bool, indicates whether the line has been properly identified
    # - type: 'A','B','C','D','E',...
    # - id: index of the line in the master table
    # - funcost: cost function associated the the line identification
    # First, initialize solution.
    solution = []
    for i in range(nlines_arc):
        solution.append({'lineok': False, 
                         'type': None,
                         'id': None, 
                         'funcost': None})

    # Type A lines.
    for i in range(2,nlines_arc-2):
        j1,j2,j3 = diagonal_ids[i]
        if j1 == j2 == j3:
            solution[i]['lineok'] = True
            solution[i]['type'] = 'A'
            solution[i]['id'] = j1
            solution[i]['funcost'] = min(diagonal_funcost[i])
    
    if ldebug:
        print('\n* Including Type A lines:')
        for i in range(nlines_arc):
            print(i, solution[i])
        if lpause:
            raw_input('press <RETURN> to continue...')

    # Type B lines.
    for i in range(2,nlines_arc-2):
        if solution[i]['lineok'] == False:
            j1,j2,j3 = diagonal_ids[i]
            f1,f2,f3 = diagonal_funcost[i]
            if j1 == j2:
                if max(f1,f2) < f3:
                    solution[i]['lineok'] = True
                    solution[i]['type'] = 'B'
                    solution[i]['id'] = j1
                    solution[i]['funcost'] = min(f1,f2)
            elif j1 == j3:
                if max(f1,f3) < f2:
                    solution[i]['lineok'] = True
                    solution[i]['type'] = 'B'
                    solution[i]['id'] = j1
                    solution[i]['funcost'] = min(f1,f3)
            elif j2 == j3:
                if max(f2,f3) < f1:
                    solution[i]['lineok'] = True
                    solution[i]['type'] = 'B'
                    solution[i]['id'] = j2
                    solution[i]['funcost'] = min(f2,f3)

    if ldebug:
        print('\n* Including Type B lines:')
        for i in range(nlines_arc):
            print(i, solution[i])
        if lpause:
            raw_input('press <RETURN> to continue...')

    # Type C lines.
    for i in range(2,nlines_arc-2):
        if solution[i]['lineok'] == False:
            j1,j2,j3 = diagonal_ids[i]
            f1,f2,f3 = diagonal_funcost[i]
            if solution[i-1]['type'] == 'B':
                if min(f2,f3) > f1:
                    solution[i]['lineok'] = True
                    solution[i]['type'] = 'C'
                    solution[i]['id'] = j1
                    solution[i]['funcost'] = f1
            elif solution[i+1]['type'] == 'B':
                if min(f1,f2) > f3:
                    solution[i]['lineok'] = True
                    solution[i]['type'] = 'C'
                    solution[i]['id'] = j3
                    solution[i]['funcost'] = f3
    
    if ldebug:
        print('\n* Including Type C lines:')
        for i in range(nlines_arc):
            print(i, solution[i])
        if lpause:
            raw_input('press <RETURN> to continue...')

    # Type D lines.
    for i in [1,nlines_arc-2]:
        j1,j2 = diagonal_ids[i]
        if j1 == j2:
            f1,f2 = diagonal_funcost[i]
            solution[i]['lineok'] = True
            solution[i]['type'] = 'D'
            solution[i]['id'] = j1
            solution[i]['funcost'] = min(f1,f2)
    
    if ldebug:
        print('\n* Including Type D lines:')
        for i in range(nlines_arc):
            print(i, solution[i])
        if lpause:
            raw_input('press <RETURN> to continue...')

    # Type E lines.
    i = 0
    if solution[i+1]['lineok'] and solution[i+2]['lineok']:
        solution[i]['lineok'] = True
        solution[i]['type'] = 'E'
        solution[i]['id'] = diagonal_ids[i][0]
        solution[i]['funcost'] = diagonal_funcost[i][0]
    i = nlines_arc-1
    if solution[i-2]['lineok'] and solution[i-1]['lineok']:
        solution[i]['lineok'] = True
        solution[i]['type'] = 'E'
        solution[i]['id'] = diagonal_ids[i][0]
        solution[i]['funcost'] = diagonal_funcost[i][0]
    
    if ldebug:
        print('\n* Including Type E lines:')
        for i in range(nlines_arc):
            print(i, solution[i])
        if lpause:
            raw_input('press <RETURN> to continue...')

    # ---
    # Check that the solutions do not contain duplicated values. If they are
    # present (probably due to the influence of an unknown line that
    # unfortunately falls too close to a real line in the master table), we
    # keep the solution with the lowest cost function. The removed lines are
    # labelled as type='R'. The procedure is repeated several times in case
    # a line appears more than twice.
    lduplicated = True
    nduplicated = 0
    while lduplicated:
        lduplicated = False
        for i1 in range(nlines_arc):
            if solution[i1]['lineok']:
                j1 = solution[i1]['id']
                for i2 in range(i1+1,nlines_arc):
                    if solution[i2]['lineok']:
                        j2 = solution[i2]['id']
                        if j1 == j2:
                            lduplicated = True
                            nduplicated += 1
                            f1 = solution[i1]['funcost']
                            f2 = solution[i2]['funcost']
                            if f1 < f2:
                                solution[i2]['lineok'] = False
                                solution[i2]['type'] = 'R'
                            else:
                                solution[i1]['lineok'] = False
                                solution[i1]['type'] = 'R'
    
    if ldebug:
        if nduplicated > 0:
            print('\n* Removing Type R lines:')
            for i in range(nlines_arc):
                print(i, solution[i])
        else:
            print('\n* No duplicated Type R lines have been found')
        if lpause:
            raw_input('press <RETURN> to continue...')

    # ---
    # Filter out points with a large deviation from a robust linear fit. The
    # filtered lines are labelled as type='T'.
    if ldebug:
        print('\n>>> Theil-Sen filtering...')
    nfit, ifit, xfit, yfit, wfit = \
      select_data_for_fit(wv_master, xpos_arc, solution)
    intercept, slope = fit_theil_sen(xfit, yfit)
    rfit = abs(yfit - (intercept + slope*xfit))
    if ldebug:
        print('rfit:', rfit)
    sigma_rfit = sigmaG(rfit)
    if ldebug:
        print('sigmag:',sigma_rfit)
    nremoved = 0
    for i in range(nfit):
        if rfit[i] > times_sigma_theil_sen*sigma_rfit:
            solution[ifit[i]]['lineok'] = False
            solution[ifit[i]]['type'] = 'T'
            nremoved += 1
    
    if ldebug:
        if nremoved > 0:
            print('\n* Removing Type T lines:')
            for i in range(nlines_arc):
                print(i, solution[i])
        else:
            print('\nNo Type T lines have been found and removed')
        if lpause:
            raw_input('press <RETURN> to continue...')

    # ---
    # Filter out points that deviates from a polynomial fit. The filtered lines
    # are labelled as type='P'.
    if ldebug:
        print('\n>>> Polynomial filtering...')
    nfit, ifit, xfit, yfit, wfit = \
      select_data_for_fit(wv_master, xpos_arc, solution)
    coeff_fit = polynomial.polyfit(xfit, yfit, poly_degree_wfit, w=1/wfit)
    poly = polynomial.Polynomial(coeff_fit)
    rfit = abs(yfit - poly(xfit))
    if ldebug:
        print('rfit:',rfit)
    sigma_rfit = sigmaG(rfit)
    if ldebug:
        print('sigmag:',sigma_rfit)
    nremoved = 0
    for i in range(nfit):
        if rfit[i] > times_sigma_polfilt*sigma_rfit:
            solution[ifit[i]]['lineok'] = False
            solution[ifit[i]]['type'] = 'P'
            nremoved += 1
    
    if ldebug:
        if nremoved > 0:
            print('\n* Removing Type P lines:')
            for i in range(nlines_arc):
                print(i, solution[i])
        else:
            print('\nNo type P lines have been found and removed')
        if lpause:
            raw_input('press <RETURN> to continue...')

    # ---
    # Include unidentified lines by using the prediction of the polynomial fit
    # to the current set of identified lines. The included lines are labelled
    # as type='I'.
    if ldebug:
        print('\n>>> Polynomial prediction of unknown lines...')
    nfit, ifit, xfit, yfit, wfit = \
      select_data_for_fit(wv_master, xpos_arc, solution)
    coeff_fit = polynomial.polyfit(xfit, yfit, poly_degree_wfit, w=1/wfit)
    poly = polynomial.Polynomial(coeff_fit)
    rfit = abs(yfit - poly(xfit))
    if ldebug:
        print('rfit:',rfit)
    sigma_rfit = sigmaG(rfit)
    if ldebug:
        print('sigmag:',sigma_rfit)

    list_id_already_found = []
    list_funcost_already_found = []
    for i in range(nlines_arc):
        if solution[i]['lineok']:
            list_id_already_found.append(solution[i]['id'])
            list_funcost_already_found.append(solution[i]['funcost'])

    nnewlines = 0
    for i in range(nlines_arc):
        if not solution[i]['lineok']:
            zfit = poly(xpos_arc[i]) # predicted wavelength
            isort = np.searchsorted(wv_master, zfit)
            if isort == 0:
                ifound = 0
                dlambda = wv_master[ifound]-zfit
            elif isort == nlines_master:
                ifound = isort - 1
                dlambda = zfit - wv_master[ifound]
            else:
                dlambda1 = zfit-wv_master[isort-1]
                dlambda2 = wv_master[isort]-zfit
                if dlambda1 < dlambda2:
                    ifound = isort - 1
                    dlambda = dlambda1
                else:
                    ifound = isort
                    dlambda = dlambda2
            if ldebug:
                print(i,zfit,ifound,dlambda)
            if ifound not in list_id_already_found:  # unused line
                if dlambda < times_sigma_inclusion*sigma_rfit:
                    list_id_already_found.append(ifound)
                    solution[i]['lineok'] = True
                    solution[i]['type'] = 'I'
                    solution[i]['id'] = ifound
                    solution[i]['funcost'] = max(list_funcost_already_found)
                    nnewlines += 1

    if ldebug:
        if nnewlines > 0:
            print('\n* Including Type I lines:')
            for i in range(nlines_arc):
                print(i, solution[i])
        else:
            print('\nNo Type I lines have been found and added')
        if lpause:
            raw_input('press <RETURN> to continue...')

    return solution

