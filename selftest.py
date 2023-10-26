# Consult Options.py/CasingTypeEnum.py/DescriptionTypeEnum.py for more info
from cron_descriptor import Options, CasingTypeEnum, DescriptionTypeEnum, ExpressionDescriptor,ExpressionSchedular
import datetime
from datetime import date

descriptor = ExpressionDescriptor(
    expression =  "*/5 15 * * THU",
    casing_type = CasingTypeEnum.Sentence,
    use_24hour_time_format = True
)
sched = ExpressionSchedular("2-59/3 1,9,22 11-26 1-10 ?", qt = datetime.date(2023,10,26))

# GetDescription uses DescriptionTypeEnum.FULL by default:

sched.get_schedule_timetable()
# Or passing Options class as second argument:

# options = Options()
# options.casing_type = CasingTypeEnum.Sentence
# options.use_24hour_time_format = True
# descriptor = ExpressionDescriptor("0 23 ? * MON-FRI", options)
# #parser = ExpressionParser("*/10 * * * *", options)
print(descriptor.get_description(DescriptionTypeEnum.FULL))


