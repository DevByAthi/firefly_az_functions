'''
Taken from this GitHub Gist: https://github.com/pktrigg/pyall/blob/master/geodetic.py
By Paul Kennedy and Jim Leven

THIS IS NOT THE ORIGINAL WORK OF ATHREYA MURALI OR ANY MEMBER OF TEAM FIREFLY.
ONLY SLIGHT MODIFICATIONS HAVE BEEN MADE FROM THE ORIGINAL CODE.
THIS IS PUBLICLY AVAILABLE CODE, ORIGINALLY WRITTEN BY THE U.S. GEOLOGICAL SURVEY IN THE EARLY 2000's
'''


# -------------------------------------------------------------------------------
# Vincenty's Direct formulae							|
# Given: latitude and longitude of a point (latitude1, longitude1) and 			|
# the geodetic azimuth (alpha1Tp2) 						|
# and ellipsoidal distance in metres (s) to a second point,			|
# 										|
# Calculate: the latitude and longitude of the second point (latitude2, longitude2) 	|
# and the reverse azimuth (alpha21).						|
# 										|
# -------------------------------------------------------------------------------
import math

FLATTENING = 1 / 298.257223563


EPSILON = 1.0e-9

MINUTE = 1.0 / 60
SECOND = 1.0 / 3600


def vincentyDirect_kennedy(latitude1, longitude1, alpha1To2, s):
    """
    Returns the lat and long of projected point and reverse azimuth
    given a reference point and a distance and azimuth to project.
    lats, longs and azimuths are passed in decimal degrees
    Returns ( latitude2,  longitude2,  alpha2To1 ) as a tuple
    """
    f = 1.0 / 298.257223563  # WGS84
    a = 6378137.0  # metres

    piD4 = math.atan(1.0)
    two_pi = piD4 * 8.0

    latitude1 = latitude1 * piD4 / 45.0
    longitude1 = longitude1 * piD4 / 45.0
    alpha1To2 = alpha1To2 * piD4 / 45.0
    if (alpha1To2 < 0.0):
        alpha1To2 = alpha1To2 + two_pi
    if (alpha1To2 > two_pi):
        alpha1To2 = alpha1To2 - two_pi

    b = a * (1.0 - f)

    TanU1 = (1 - f) * math.tan(latitude1)
    U1 = math.atan(TanU1)
    sigma1 = math.atan2(TanU1, math.cos(alpha1To2))
    Sinalpha = math.cos(U1) * math.sin(alpha1To2)
    cosalpha_sq = 1.0 - Sinalpha * Sinalpha

    u2 = cosalpha_sq * (a * a - b * b) / (b * b)
    A = 1.0 + (u2 / 16384) * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = (u2 / 1024) * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))

    # Starting with the approximation
    sigma = (s / (b * A))

    last_sigma = 2.0 * sigma + 2.0  # something impossible

    if sigma <= EPSILON:
        two_sigma_m = 2 * sigma1

    # Iterate the following three equations
    #  until there is no significant change in sigma

    # two_sigma_m , delta_sigma
    while sigma > EPSILON and abs((last_sigma - sigma) / sigma) > EPSILON:
        two_sigma_m = 2 * sigma1 + sigma

        delta_sigma = B * math.sin(sigma) * (math.cos(two_sigma_m) + (B / 4) * (math.cos(sigma) * (-1 + 2 * math.pow(math.cos(two_sigma_m), 2) - (B / 6) * math.cos(two_sigma_m) * (-3 + 4 * math.pow(math.sin(sigma), 2)) * (-3 + 4 * math.pow(math.cos(two_sigma_m), 2)))))
        last_sigma = sigma
        sigma = (s / (b * A)) + delta_sigma

    latitude2 = math.atan2((math.sin(U1) * math.cos(sigma) + math.cos(U1) * math.sin(sigma) * math.cos(alpha1To2)),
                           ((1 - f) * math.sqrt(math.pow(Sinalpha, 2) +
                                                pow(math.sin(U1) * math.sin(sigma) - math.cos(U1) * math.cos(
                                                    sigma) * math.cos(alpha1To2), 2))))

    lembda = math.atan2((math.sin(sigma) * math.sin(alpha1To2)), (math.cos(U1) * math.cos(sigma) -
                                                                  math.sin(U1) * math.sin(sigma) * math.cos(alpha1To2)))

    C = (f / 16) * cosalpha_sq * (4 + f * (4 - 3 * cosalpha_sq))

    omega = lembda - (1 - C) * f * Sinalpha * (sigma + C * math.sin(sigma) * (math.cos(two_sigma_m) + C * math.cos(sigma) * (-1 + 2 * math.pow(math.cos(two_sigma_m), 2))))

    longitude2 = longitude1 + omega

    alpha21 = math.atan2(Sinalpha, (-math.sin(U1) * math.sin(sigma) + math.cos(U1) * math.cos(sigma) * math.cos(alpha1To2)))

    alpha21 = alpha21 + two_pi / 2.0
    if (alpha21 < 0.0):
        alpha21 = alpha21 + two_pi
    if (alpha21 > two_pi):
        alpha21 = alpha21 - two_pi

    latitude2 = latitude2 * 45.0 / piD4
    longitude2 = longitude2 * 45.0 / piD4
    alpha21 = alpha21 * 45.0 / piD4

    return latitude2, longitude2, alpha21

    # END of Vincenty's Direct formulae


if __name__ == '__main__':
    print("Testing Vincenty's Direct Formula")

    '''
    Test case (from Geoscience Australia), using WGS-84:
    
    Flinders Peak	37°57′03.72030″S, 144°25′29.52440″E
    Buninyong	37°39′10.15610″S, 143°55′35.38390″E
    s	54 972.271 m
    α1	306°52′05.37″
    α2	127°10′25.07″ (= 307°10′25.07″ p1->p2)

    '''
    flinders_lat = -(37 + 57 * MINUTE + 3.72030 * SECOND)
    flinders_long = (144 + 25 * MINUTE + 29.52440 * SECOND)

    buninyong_lat = -(37 + 39 * MINUTE + 10.15610 * SECOND)
    buninyong_long = (143 + 55 * MINUTE + 35.38390 * SECOND)
    expected_return_bearing = (127 + 10 * MINUTE + 25.07 * SECOND)  # 307° 10′ 25.07″

    dist = 54972.271
    bearing = (306 + 52 * MINUTE + 5.37 * SECOND)  # 306° 52′ 05.37

    lat, lon, a = vincentyDirect_kennedy(flinders_lat, flinders_long, bearing, dist)

    print(lat, lon, a)
    print(buninyong_lat, buninyong_long, expected_return_bearing)
