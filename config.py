# LinkedIn 配置
LINKEDIN_URL = "https://www.linkedin.com/jobs/search/"

# 搜索参数 - 根据需要修改
SEARCH_PARAMS = {
    "keywords": "data","solution",  # 搜索关键词
    "location": "Berlin",      # 地点
    "f_WT": "1",                      # 远程工作 (2=远程)
    "f_E": "2,3",                   # 经验级别 (2=初级, 3=中级, 4=高级)
    "f_TPR": "r86400",                # 过去24小时发布的职位
    "f_JT": "F",                      # 职位类型 (F=全职)
    "f_AL": "false",                   # 易申请
}

# 筛选条件
JOB_CRITERIA = {
    "required_skills": ["python", "sql", "analysis", "sql", "aws"],
    "min_salary_mention": False,       # 是否要求提及薪资
    "sponsorship_mention": False,      # 是否要求提及签证赞助
    "english_only": True,             # 只要英文职位描述
    "min_description_length": 200,    # 最小描述长度
}

# 语言检测配置
ENGLISH_KEYWORDS = [
    "experience", "skills", "development", "team", "project",
    "requirements", "responsibilities", "software", "engineering"
]

# Selenium 配置
WEBDRIVER_CONFIG = {
    "headless": False,  # 设置为 True 在后台运行
    "timeout": 30,
    "implicit_wait": 10
}
