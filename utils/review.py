# -*- coding: utf-8 -*-

# import tiktoken
import openai
from json import dump, loads

try:
    from utils.config import Prompts, OPENAI_KEY, REVIEW_MODEL
except ImportError:
    from utils.config_sample import Prompts, OPENAI_KEY, REVIEW_MODEL

# def num_tokens_from_messages(messages, model="gpt-3.5-turbo-0301"):
#     '''
#     Returns the number of tokens used by a list of messages.
#     官方给的token计算示例, 
#     '''
#     try:
#         encoding = tiktoken.encoding_for_model(model)
#     except KeyError:
#         encoding = tiktoken.get_encoding("cl100k_base")
#     if model == "gpt-3.5-turbo-0301":  # note: future models may deviate from this
#         num_tokens = 0
#         for message in messages:
#             num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
#             for key, value in message.items():
#                 num_tokens += len(encoding.encode(value))
#                 if key == "name":  # if there's a name, the role is omitted
#                     num_tokens += -1  # role is always required and always 1 token
#         num_tokens += 2  # every reply is primed with <im_start>assistant
#         return num_tokens
#     else:
#         raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.""")


class Reviewer:
    '''
    调用chatGPT进行文献内容查看:
    1. 文献总结: 将不超过10篇的文献摘要总结为一段话
    2. 文献内容判断, 根据自定义的Promot判断, 文献是否符合准入标准
    '''
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key if api_key else OPENAI_KEY
        self.model = model if model else REVIEW_MODEL
        self.messages = None


    def query(self):
        '''
        发送请求并获取chatGPT给的结果
        '''
        # 设置email和搜索关键词
        openai.api_key = self.api_key
        response = openai.ChatCompletion.create(
            model = self.model,
            messages = self.messages
        )

        return response


    def screen(self, criterias, abstract):
        '''
        meta分析时用的方法, 读取标准内容和文献摘要后,
        判断文章是否符合准入标准
        '''
        message = Prompts['Screen'].format(criterias=criterias, abstract=abstract)
        self.messages = [
            {"role": "user", "content": message},
        ]

        return self.query()


    def summarise(self, papers):
        '''
        meta分析时用的方法, 读取标准内容和文献摘要后,
        判断文章是否符合准入标准
        '''
        units = []
        for idx, abstract in papers:
            units.append(Prompts['Summarize_Unit'].format(idx=idx, abstract=abstract))
        units.append(Prompts['Summarize'].format(idx=len(papers)))
        
        message = '\n'.join(units)
        self.messages = [
            {"role": "user", "content": message},
        ]

        return self.query()


def screen_demo():
    reviewer = Reviewer()
    criterias = '''
        1. 文献是研究成果文献, 不可以是Meta分析或者文献综述
        2. 文献的研究内容不是减肥手术、体重干预等对疾病影响
        3. 文献的研究对象不可以包含男性, 必须全部是女性
    '''
    abstract = '''
        Objective: To assess the separate and combined associations of maternal pre-pregnancy body mass index (BMI) and gestational weight gain with the risks of pregnancy complications and their population impact.
        Design: Individual participant data meta-analysis of 39 cohorts.
        Setting: Europe, North America, and Oceania.
        Population: 265 270 births.
        Methods: Information on maternal pre-pregnancy BMI, gestational weight gain, and pregnancy complications was obtained. Multilevel binary logistic regression models were used.
        Main outcome measures: Gestational hypertension, pre-eclampsia, gestational diabetes, preterm birth, small and large for gestational age at birth.
        Results: Higher maternal pre-pregnancy BMI and gestational weight gain were, across their full ranges, associated with higher risks of gestational hypertensive disorders, gestational diabetes, and large for gestational age at birth. Preterm birth risk was higher at lower and higher BMI and weight gain. Compared with normal weight mothers with medium gestational weight gain, obese mothers with high gestational weight gain had the highest risk of any pregnancy complication (odds ratio 2.51, 95% CI 2.31- 2.74). We estimated that 23.9% of any pregnancy complication was attributable to maternal overweight/obesity and 31.6% of large for gestational age infants was attributable to excessive gestational weight gain.
        Conclusions: Maternal pre-pregnancy BMI and gestational weight gain are, across their full ranges, associated with risks of pregnancy complications. Obese mothers with high gestational weight gain are at the highest risk of pregnancy complications. Promoting a healthy pre-pregnancy BMI and gestational weight gain may reduce the burden of pregnancy complications and ultimately the risk of maternal and neonatal morbidity.
    '''
    # 返回的内容直接解析为Python对象了
    response = reviewer.screen(criterias, abstract)
    with open('demo.json', 'w') as rJson:
        dump(response, rJson)
    
    answer = loads(response['choices'][0]['message']['content'])
    print(answer)
    with open('answer.json', 'w') as aJson:
        dump(answer, aJson)


if __name__ == '__main__':
    reviewer = Reviewer()
    papers = [
        ('12345', 'Background: Little is known about reproductive health in severely obese women. In this study, we present associations between different levels of severe obesity and a wide range of health outcomes in the mother and child. Method(s): From the Danish National Birth Cohort, we obtained self-reported information about prepregnant body mass index (BMI) for 2451 severely obese women and 2450 randomly selected women from the remaining cohort who served as a comparison group. Information about maternal and infant outcomes was also self-reported or came from registers. Logistic regression was used to estimate the association between different levels of severe obesity and reproductive outcomes. Principal Findings: Subfecundity was more frequent in severely obese women, and during pregnancy, they had an excess risk of urinary tract infections, gestational diabetes, preeclampsia and other hypertensive disorders which increased with severity of obesity. They tended to have a higher risk of both pre- and post-term birth, and risk of cesarean and instrumental deliveries increased across obesity categories. After birth, severely obese women more often failed to initiate or sustain breastfeeding. Risk of weight retention 1.5 years after birth was similar to that of other women, but after adjustment for gestational weight gain, the risk was increased, especially in women in the lowest obesity category. In infants, increasing maternal obesity was associated with decreased risk of a low birth weight and increased risk of a high birth weight. Estimates for ponderal index showed the same pattern indicating an increasing risk of neonatal fatness with severity of obesity. Infant obesity measured one year after birth was also increased in children of severely obese mothers. Conclusion(s): Severe obesity is correlated with a substantial disease burden in reproductive health. Although the causal mechanisms remain elusive, these findings are useful for making predictions and planning health care at the individual level. © 2009 Nohr et al.'),
        ('45456', 'Background: Preeclampsia is one of the leading causes of maternal and perinatal morbidity and mortality world-wide. The risk for developing preeclampsia varies depending on the underlying mechanism. Because the disorder is heterogeneous, the pathogenesis can differ in women with various risk factors. Understanding these mechanisms of disease responsible for preeclampsia as well as risk assessment is still a major challenge. The aim of this study was to determine the risk factors associated with preeclampsia, in healthy women in maternity hospitals of Karachi and Rawalpindi. Method(s): We conducted a hospital based matched case-control study to assess the factors associated with preeclampsia in Karachi and Rawalpindi, from January 2006 to December 2007. 131 hospital-reported cases of PE and 262 controls without history of preeclampsia were enrolled within 3 days of delivery. Cases and controls were matched on the hospital, day of delivery and parity. Potential risk factors for preeclampsia were ascertained during in-person postpartum interviews using a structured questionnaire and by medical record abstraction. Conditional logistic regression was used to estimate matched odds ratios (ORs) and 95% confidence intervals (95% CIs). Result(s): In multivariate analysis, women having a family history of hypertension (adjusted OR 2.06, 95% CI; 1.27-3.35), gestational diabetes (adjusted OR 6.57, 95% CI; 1.94 -22.25), pre-gestational diabetes (adjusted OR 7.36, 95% CI; 1.37-33.66) and mental stress during pregnancy (adjusted OR 1.32; 95% CI; 1.19-1.46, for each 5 unit increase in Perceived stress scale score) were at increased risk of preeclampsia. However, high body mass index, maternal age, urinary tract infection, use of condoms prior to index pregnancy and sociodemographic factors were not associated with higher risk of having preeclampsia. Conclusion(s): Development of preeclampsia was associated with gestational diabetes, pregestational diabetes, family history of hypertension and mental stress during pregnancy. These factors can be used as a screening tool for preeclampsia prediction. Identification of the above mentioned predictors would enhance the ability to diagnose and monitor women likely to develop preeclampsia before the onset of disease for timely interventions and better maternal and fetal outcomes. © 2010 Shamsi et al; licensee BioMed Central Ltd.'),
    ]
    reviewer.summarise(papers)
