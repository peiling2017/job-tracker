import re
import pandas as pd
from typing import Dict, List, Tuple
import nltk
from bs4 import BeautifulSoup

# 下载NLTK数据（第一次运行需要）
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class JobAnalyzer:
    def __init__(self, criteria: Dict):
        self.criteria = criteria
        
    def is_english_job_description(self, text: str) -> bool:
        """检测职位描述是否为英文"""
        if not text:
            return False
            
        # 检查常见英文单词
        english_patterns = [
            r'\bexperience\b', r'\bskills\b', r'\bdevelopment\b', 
            r'\bteam\b', r'\bproject\b', r'\brequirements\b',
            r'\bresponsibilities\b', r'\bsoftware\b', r'\bengineering\b'
        ]
        
        english_count = sum(1 for pattern in english_patterns 
                          if re.search(pattern, text.lower()))
        
        # 如果找到足够多的英文关键词，认为是英文职位
        return english_count >= 5
    
    def analyze_job_description(self, description: str) -> Dict:
        """分析职位描述"""
        if not description:
            return {"is_qualified": False, "reason": "No description"}
        
        # 清理HTML标签
        soup = BeautifulSoup(description, 'html.parser')
        clean_text = soup.get_text().lower()
        
        # 检查是否为英文
        if self.criteria.get("english_only", True):
            if not self.is_english_job_description(clean_text):
                return {"is_qualified": False, "reason": "Not English job description"}
        
        # 检查技能匹配
        required_skills = self.criteria.get("required_skills", [])
        matched_skills = []
        missing_skills = []
        
        for skill in required_skills:
            if re.search(r'\b' + re.escape(skill.lower()) + r'\b', clean_text):
                matched_skills.append(skill)
            else:
                missing_skills.append(skill)
        
        
        
      
    
        
        return {
            "is_qualified": is_qualified,
            "skill_match_ratio": skill_match_ratio,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "salary_mentioned": salary_mentioned,
            "sponsorship_mentioned": sponsorship_mentioned,
            "is_english": self.is_english_job_description(clean_text),
            "rejection_reason": "; ".join(reasons) if reasons else "Qualified"
        }
    
    def save_to_excel(self, jobs_data: List[Dict], filename: str = "linkedin_jobs.xlsx"):
        """保存职位数据到Excel"""
        if not jobs_data:
            print("No data to save")
            return
        
        df = pd.DataFrame(jobs_data)
        
        # 重新排列列的顺序
        columns_order = [
            'title', 'company', 'location', 'is_qualified', 'skill_match_ratio',
            'salary_mentioned', 'sponsorship_mentioned', 'is_english',
            'matched_skills', 'missing_skills', 'rejection_reason', 'job_url'
        ]
        
        # 只保留存在的列
        existing_columns = [col for col in columns_order if col in df.columns]
        other_columns = [col for col in df.columns if col not in columns_order]
        
        df = df[existing_columns + other_columns]
        
        # 保存到Excel
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='All Jobs', index=False)
            
            # 创建合格职位的sheet
            qualified_jobs = df[df['is_qualified'] == True]
            qualified_jobs.to_excel(writer, sheet_name='Qualified Jobs', index=False)
        
        print(f"数据已保存到 {filename}")
        print(f"总职位数: {len(df)}")
        print(f"合格职位数: {len(qualified_jobs)}")
