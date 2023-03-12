# -*- coding: utf-8 -*-

# import tiktoken
from utils.config import API_KEY, MODEL, Promots
import openai
from json import dump, loads

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
    def __init__(self, model=MODEL):
        self.api_key = API_KEY
        self.model = model
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
        message = Promots['Criteria'].format(criterias=criterias, abstract=abstract)
        self.messages = [
            {"role": "user", "content": message},
        ]

        return self.query()


        


if __name__ == '__main__':
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
