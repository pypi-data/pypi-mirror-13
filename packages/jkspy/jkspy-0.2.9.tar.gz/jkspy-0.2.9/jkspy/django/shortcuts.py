from django.db import models

#### Search helper
### Criterion Building
def makeSearchCriterion(searchword, fields):
    words = searchword.split(" ")
    model_criterion = models.Q()
    for field_criterion in fields:
        sub_criterion = models.Q()
        for word in words:
            sub_criterion = sub_criterion & models.Q(**{field_criterion+"__contains": word})
        model_criterion = model_criterion | sub_criterion
            
    return model_criterion