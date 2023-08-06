import facerec2010
import bob.bio.csu

preprocessor = bob.bio.csu.preprocessor.LDAIR(
    REGION_ARGS = facerec2010.baseline.lda.CohortLDA_REGIONS,
    REGION_KEYWORDS = facerec2010.baseline.lda.CohortLDA_KEYWORDS
)
