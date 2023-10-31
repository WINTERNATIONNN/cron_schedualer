# Consult Options.py/CasingTypeEnum.py/DescriptionTypeEnum.py for more info
from cron_descriptor import Options, CasingTypeEnum, DescriptionTypeEnum, ExpressionDescriptor,ExpressionSchedular
import datetime
from datetime import date
import json

EXPRESSION = "*/5 15 * * MON-FRI" #"0 23 ? * MON-FRI"
descriptor = ExpressionDescriptor(
    expression = EXPRESSION,
    casing_type = CasingTypeEnum.Sentence,
    use_24hour_time_format = True
)
sched = ExpressionSchedular(EXPRESSION, qt = datetime.date(2023,10,26))
print(descriptor.get_description(DescriptionTypeEnum.FULL))
print([i.strftime("%H:%M:%S") for i in sched.get_schedule_timetable()])


# GetDescription uses DescriptionTypeEnum.FULL by default:

# Or passing Options class as second argument:

# options = Options()
# options.casing_type = CasingTypeEnum.Sentence
# options.use_24hour_time_format = True
# descriptor = ExpressionDescriptor("0 23 ? * MON-FRI", options)
# #parser = ExpressionParser("*/10 * * * *", options)
#print(descriptor.get_description(DescriptionTypeEnum.FULL))




