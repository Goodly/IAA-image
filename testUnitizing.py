import sys
from jnius import autoclass

def testUnitizing():
    UAS = autoclass('org.dkpro.statistics.agreement.unitizing.UnitizingAnnotationStudy')
    # raterCount, length
    study = UAS(2, 20)
    # offset, length, rater, category
    study.addUnit(4,2,1, "a")
    study.addUnit(4,2,2, "a")
    study.addUnit(10,3,1, "B")
    study.addUnit(0,3,2, "B")
    KAUA = autoclass('org.dkpro.statistics.agreement.unitizing.KrippendorffAlphaUnitizingAgreement')
    alpha = KAUA(study)
    print(alpha.calculateCategoryAgreement("a"))
    print(alpha.calculateCategoryAgreement("B"))
    UMP = autoclass('org.dkpro.statistics.agreement.visualization.UnitizingMatrixPrinter')
    USP = autoclass('org.dkpro.statistics.agreement.visualization.UnitizingStudyPrinter')
    ump = UMP()
    System = autoclass('java.lang.System')
    ump.print(System.out, study,  "a", 2, 1)
    ump.print(System.out, study,  "B", 2, 1)
    USP().print(System.out, study)
    USP().printUnitsForCategory(System.out, study, "a", "a")
    USP().printUnitsForCategory(System.out, study, "B", "B")

if __name__ == "__main__":
    testUnitizing()
