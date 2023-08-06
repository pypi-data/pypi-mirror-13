import facerec2010
import bob.bio.csu

algorithm = bob.bio.csu.algorithm.LDAIR(
    REGION_ARGS = facerec2010.baseline.lda.CohortLDA_REGIONS,
    REGION_KEYWORDS = facerec2010.baseline.lda.CohortLDA_KEYWORDS
)
