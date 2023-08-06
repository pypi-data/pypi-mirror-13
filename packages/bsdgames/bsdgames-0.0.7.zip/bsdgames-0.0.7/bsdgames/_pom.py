import sys
import time
import math


class Pom:
    PI = 3.14159265358979323846
    EPOCH_MINUS_1970 = (20 * 365 + 5 - 1)  # 20 years, 5 leaps, back 1 day to Jan 0
    EPSILONg = 279.403303  # solar ecliptic long at EPOCH
    RHOg = 282.768422  # solar ecliptic long of perigee at EPOCH
    ECCEN = 0.016713  # solar orbit eccentricity
    lzero = 318.351648  # lunar mean long at EPOCH
    Pzero = 36.340410  # lunar mean long of perigee at EPOCH
    Nzero = 318.510107  # lunar mean long of node at EPOCH

    def __init__(self):
        self.pom()

    def adj360(self, deg):
        while (deg < 0 or deg > 360):
            if deg < 0:
                deg += 360
            elif deg > 360:
                deg -= 360
        # print 'kkk',deg
        return deg

    def dotr(self, deg):
        return self.PI * (deg / 180)

    def potm(self, days):
        N = 360 * days / 365.242191  # sec 46 #3
        N = self.adj360(N)
        # print N
        # print type(N)
        # print type(self.EPSILONg)
        Msol = N + self.EPSILONg - self.RHOg  # sec 46 #4
        Msol = self.adj360(Msol)
        Ec = 360 / self.PI * self.ECCEN * math.sin(self.dotr(Msol))  # sec 46 #5
        LambdaSol = N + Ec + self.EPSILONg  # sec 46 #6
        LambdaSol = self.adj360(LambdaSol)
        l = 13.1763966 * days + self.lzero  # sec 65 #4
        l = self.adj360(l)
        Mm = l - (0.1114041 * days) - self.Pzero  # sec 65 #5
        Mm = self.adj360(Mm)
        Nm = self.Nzero - (0.0529539 * days)  # sec 65 #6
        Nm = self.adj360(Nm)
        Ev = 1.2739 * math.sin(self.dotr(2 * (l - LambdaSol) - Mm))  # sec 65 #7
        Ac = 0.1858 * math.sin(self.dotr(Msol))  # sec 65 #8
        A3 = 0.37 * math.sin(self.dotr(Msol))
        Mmprime = Mm + Ev - Ac - A3  # sec 65 #9
        Ec = 6.2886 * math.sin(self.dotr(Mmprime))  # sec 65 #10
        A4 = 0.214 * math.sin(self.dotr(2 * Mmprime))  # sec 65 #11
        lprime = l + Ev + Ec - Ac + A4  # sec 65 #12
        V = 0.6583 * math.sin(self.dotr(2 * (lprime - LambdaSol)))  # sec 65 #13
        ldprime = lprime + V  # sec 65 #14
        D = ldprime - LambdaSol  # sec 67 #2
        return 50.0 * (1 - math.cos(self.dotr(D)))  # sec 67 #3

    def pom(self):
        argv = sys.argv[1:]
        print "Today is",
        str = 'None'
        now = time.time()
        # print time.ctime(time.time())

        # tmpt = time.time() + 8*3600
        tmpt = time.time()
        days = (tmpt - self.EPOCH_MINUS_1970 * 86400) / 86400.0
        today = self.potm(days) + 0.5
        if int(today) == 100:
            print 'Full'
        elif int(today) == 0:
            print 'New'
        else:
            tomorrow = self.potm(days + 1)
            if int(today) == 50:
                if tomorrow > today:
                    print  "at the First Quarter"
                else:
                    print  "at the Last Quarter"
            else:
                today -= 0.5
                if tomorrow > today:
                    print  "Waxing",
                else:
                    print  "Waning",
                if today > 50:
                    print 'Gibbous (%1.0f%% of Full)' % today
                elif today < 50:
                    print 'Crescent (%1.0f%% of Full)' % today



if __name__ == '__main__':
    pom = Pom()
    argv = sys.argv[1:]
    print "Today is",
    str = 'None'
    now = time.time()
    # print time.ctime(time.time())

    # tmpt = time.time() + 8*3600
    tmpt = time.time()
    days = (tmpt - pom.EPOCH_MINUS_1970 * 86400) / 86400.0
    today = pom.potm(days) + 0.5
    if int(today) == 100:
        print 'Full'
    elif int(today) == 0:
        print 'New'
    else:
        tomorrow = pom.potm(days + 1)
        if int(today) == 50:
            if tomorrow > today:
                print  "at the First Quarter"
            else:
                print  "at the Last Quarter"
        else:
            today -= 0.5
            if tomorrow > today:
                print  "Waxing",
            else:
                print  "Waning",
            if today > 50:
                print 'Gibbous (%1.0f%% of Full)' % today
            elif today < 50:
                print 'Crescent (%1.0f%% of Full)' % today

