# Consult Options.py/CasingTypeEnum.py/DescriptionTypeEnum.py for more info
from cron_descriptor import Options, CasingTypeEnum, DescriptionTypeEnum, ExpressionDescriptor,ExpressionSchedular
import datetime
from datetime import date

descriptor = ExpressionDescriptor(
    expression =  "0 23 ? * MON-FRI",
    casing_type = CasingTypeEnum.Sentence,
    use_24hour_time_format = True
)
sched = ExpressionSchedular(expression = "0 23 ? * TUE-FRI", qt = datetime.date(2023,10,23))

# GetDescription uses DescriptionTypeEnum.FULL by default:
print(descriptor.get_description())
print("{}".format(descriptor))
print(sched.get_next_schedule_time())
# Or passing Options class as second argument:

options = Options()
options.casing_type = CasingTypeEnum.Sentence
options.use_24hour_time_format = True
descriptor = ExpressionDescriptor("0 23 ? * MON-FRI", options)
#parser = ExpressionParser("*/10 * * * *", options)
print(descriptor.get_description(DescriptionTypeEnum.FULL))


