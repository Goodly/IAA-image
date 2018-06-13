import sys
from jnius import autoclass

def testUnitizing():
    UAS = autoclass('org.dkpro.statistics.agreement.unitizing.UnitizingAnnotationStudy')
    # raterCount, length
    study = UAS(1500, 200)
    # offset, length, rater, category
    study.addUnit(4,2,1, "a")
    study.addUnit(4,2,2, "a")
    study.addUnit(4,2,3, "a")
    study.addUnit(4,2,4, "a")
    study.addUnit(4,2,5, "a")
    study.addUnit(4,2,6, "a")
    study.addUnit(4,2,7, "a")
    study.addUnit(4,2,8, "a")
    study.addUnit(4,2,1, "b")
    study.addUnit(4,2,2, "b")
    study.addUnit(4,2,3, "b")
    study.addUnit(4,2,4, "b")
    study.addUnit(4,2,5, "b")
    study.addUnit(4,2,6, "b")
    study.addUnit(4,2,7, "b")
    study.addUnit(4,2,8, "b")
    for i in range(1500):
        study.addUnit(4,2,i+9,"a")
        study.addUnit(4,2,i+9,"b")
    # study.addUnit(10,3,1, "B")
    # study.addUnit(0,3,2, "B")
    #study.addUnit(0,0,1, "a")
    KAUA = autoclass('org.dkpro.statistics.agreement.unitizing.KrippendorffAlphaUnitizingAgreement')
    alpha = KAUA(study)
    print(alpha.calculateCategoryAgreement("a"))
    print(alpha.calculateCategoryAgreement("b"))
    # UMP = autoclass('org.dkpro.statistics.agreement.visualization.UnitizingMatrixPrinter')
    # USP = autoclass('org.dkpro.statistics.agreement.visualization.UnitizingStudyPrinter')
    # ump = UMP()
    # System = autoclass('java.lang.System')
    # ump.print(System.out, study,  "a", 2, 1)
    # ump.print(System.out, study,  "B", 2, 1)
    # USP().print(System.out, study)
    # USP().printUnitsForCategory(System.out, study, "a", "a")
    # USP().printUnitsForCategory(System.out, study, "B", "B")

if __name__ == "__main__":
    testUnitizing()
