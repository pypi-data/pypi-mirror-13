import facerec2010
import bob.bio.csu

algorithm = bob.bio.csu.algorithm.LRPCA(
    TUNING = facerec2010.baseline.lrpca.GBU_TUNING
)
