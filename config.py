# LinkedIn 搜索配置
LINKEDIN_URL = "https://www.linkedin.com/jobs/search/"

# 基本搜索参数
SEARCH_PARAMS = {
    "keywords": "software engineer",  # 搜索关键词
    "location": "United States",      # 地点
    "f_TPR": "r86400",               # 过去24小时发布的职位
    "f_WT": "2",                     # 远程工作选项
    "f_JT": "F",                     # 职位类型: F=全职
}

# 工作地点筛选 (根据需要修改)
LOCATION_FILTER = {
    "allowed_countries": ["United States", "Canada", "United Kingdom", "Australia"],
    "work_arrangement": ["remote", "hybrid", "on-site"]  # 全部接受
}

# 英文检测配置
ENGLISH_DETECTION = {
    "min_english_score": 0.7,  # 英文检测阈值
    "required_keywords": [
        "experience", "skills", "development", "team", "project",
        "requirements", "responsibilities", "software", "engineering",
        "design", "implementation", "analysis", "management"
    ]
}

# 浏览器配置
BROWSER_CONFIG = {
    "headless": False,
    "timeout": 20,
    "implicit_wait": 5
}
