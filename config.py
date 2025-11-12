# LinkedIn 搜索配置
LINKEDIN_URL = "https://www.linkedin.com/jobs/search/"

# 搜索参数 - 德国五大城市，现场/混合办公
SEARCH_PARAMS = {
    "keywords": "software engineer developer IT",
    "location": "Düsseldorf, Berlin, Munich, Frankfurt, Leipzig, Germany",
    "f_TPR": "r86400",               # 过去24小时发布的职位
    "f_WT": "1,3",                   # 工作类型: 1=现场办公, 3=混合办公
    "f_JT": "F",                     # 职位类型: F=全职
}

# 工作地点筛选
LOCATION_FILTER = {
    "allowed_cities": ["Düsseldorf", "Berlin", "Munich", "Frankfurt", "Leipzig"],
    "work_arrangement": ["hybrid", "on-site"]  # 只要混合和现场办公
}

# 英文检测配置
ENGLISH_DETECTION = {
    "min_english_score": 0.7,
    "required_keywords": [
        "experience", "skills", "development", "team", "project",
        "requirements", "responsibilities", "software", "engineering",
        "design", "implementation", "analysis", "management"
    ]
}

# 安全保护配置 - 保守方案
SAFETY_CONFIG = {
    "max_jobs_per_session": 20,       # 每次会话最多20个职位
    "delay_between_jobs": [4, 10],    # 职位间延迟4-10秒
    "session_break_after": 10,        # 每10个职位休息一次
    "break_duration": [30, 60],       # 休息30-60秒
    "max_sessions_per_day": 3,        # 每天最多3次会话
    "min_session_interval": 14400,    # 会话间隔4小时(秒)
}

# 浏览器配置
BROWSER_CONFIG = {
    "headless": False,                # 显示浏览器窗口
    "timeout": 25,
    "implicit_wait": 8
}
