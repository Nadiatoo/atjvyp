#!/usr/bin/env python3
"""
Skill注册表管理器
用于管理所有skill的注册、发现、调用和状态监控
"""

import json
import os
import sys
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

class SkillRegistry:
    def __init__(self, registry_path: str = None):
        """初始化注册表管理器"""
        if registry_path is None:
            # 默认路径
            self.workspace = os.path.expanduser("~/.openclaw/workspace")
            self.registry_path = os.path.join(self.workspace, "skill_registry.json")
        else:
            self.registry_path = registry_path
            self.workspace = os.path.dirname(registry_path)
        
        self.skills_dir = os.path.expanduser("~/.openclaw/skills")
        self.system_skills_dir = "/opt/homebrew/lib/node_modules/openclaw/skills"
        
        # 加载或创建注册表
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """加载注册表文件"""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"加载注册表失败: {e}")
                return self._create_empty_registry()
        else:
            return self._create_empty_registry()
    
    def _create_empty_registry(self) -> Dict:
        """创建空的注册表结构"""
        return {
            "schema_version": "1.0",
            "last_updated": datetime.now().isoformat(),
            "registry": {},
            "categories": {
                "system": "系统管理类skill",
                "finance": "金融交易类skill",
                "data": "数据处理类skill",
                "communication": "通讯工具类skill",
                "productivity": "生产力工具类skill",
                "development": "开发工具类skill",
                "media": "媒体处理类skill",
                "ai": "人工智能类skill"
            },
            "statistics": {
                "total_skills": 0,
                "by_category": {cat: 0 for cat in self._create_empty_registry()["categories"]},
                "active_skills": 0,
                "inactive_skills": 0
            }
        }
    
    def save_registry(self):
        """保存注册表到文件"""
        self.registry["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(self.registry, f, ensure_ascii=False, indent=2)
            print(f"注册表已保存到: {self.registry_path}")
            return True
        except Exception as e:
            print(f"保存注册表失败: {e}")
            return False
    
    def scan_skills(self, force_rescan: bool = False):
        """扫描所有可用的skill"""
        print("开始扫描skill...")
        
        # 扫描用户安装的skill
        user_skills = self._scan_skill_directory(self.skills_dir, "user")
        print(f"发现用户skill: {len(user_skills)}个")
        
        # 扫描系统skill
        system_skills = self._scan_skill_directory(self.system_skills_dir, "system")
        print(f"发现系统skill: {len(system_skills)}个")
        
        # 合并skill
        all_skills = {**user_skills, **system_skills}
        
        # 更新注册表
        updated = False
        for skill_id, skill_info in all_skills.items():
            if skill_id not in self.registry["registry"] or force_rescan:
                self.registry["registry"][skill_id] = skill_info
                updated = True
        
        if updated:
            # 更新统计信息
            self._update_statistics()
            self.save_registry()
            print(f"注册表已更新，共 {len(self.registry['registry'])} 个skill")
        else:
            print("没有发现新的skill")
    
    def _scan_skill_directory(self, directory: str, source: str) -> Dict:
        """扫描指定目录下的skill"""
        skills = {}
        
        if not os.path.exists(directory):
            return skills
        
        # 查找所有SKILL.md文件
        skill_files = glob.glob(os.path.join(directory, "**", "SKILL.md"), recursive=True)
        
        for skill_file in skill_files:
            skill_dir = os.path.dirname(skill_file)
            skill_name = os.path.basename(skill_dir)
            skill_id = f"{source}_{skill_name}"
            
            try:
                # 读取SKILL.md文件
                with open(skill_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 解析skill信息
                skill_info = self._parse_skill_info(content, skill_dir, skill_name, source)
                skills[skill_id] = skill_info
                
            except Exception as e:
                print(f"解析skill失败 {skill_file}: {e}")
        
        return skills
    
    def _parse_skill_info(self, content: str, skill_dir: str, skill_name: str, source: str) -> Dict:
        """从SKILL.md内容中解析skill信息"""
        # 简单解析，实际可以更复杂
        lines = content.split('\n')
        description = ""
        in_description = False
        
        for line in lines:
            if line.startswith("# "):
                name = line[2:].strip()
            elif "description" in line.lower() and ":" in line:
                # 尝试提取描述
                parts = line.split(":", 1)
                if len(parts) > 1:
                    description = parts[1].strip()
            elif line.strip().startswith("<description>"):
                in_description = True
            elif line.strip().startswith("</description>"):
                in_description = False
            elif in_description:
                description += line.strip() + " "
        
        # 确定分类
        category = self._guess_category(skill_name, description)
        
        return {
            "name": skill_name.replace("-", " ").title(),
            "description": description.strip() or f"{skill_name} skill",
            "category": category,
            "location": skill_dir,
            "source": source,
            "status": "active",
            "version": "1.0",
            "dependencies": [],
            "tags": [category, source],
            "usage_count": 0,
            "last_used": None,
            "registered_at": datetime.now().isoformat()
        }
    
    def _guess_category(self, skill_name: str, description: str) -> str:
        """根据skill名称和描述猜测分类"""
        skill_name_lower = skill_name.lower()
        desc_lower = description.lower()
        
        # 金融交易类
        finance_keywords = ["finance", "stock", "market", "trade", "投资", "股票", "交易", "彪哥"]
        if any(keyword in skill_name_lower or keyword in desc_lower for keyword in finance_keywords):
            return "finance"
        
        # 系统管理类
        system_keywords = ["system", "管理", "registry", "skill", "工具", "manager"]
        if any(keyword in skill_name_lower or keyword in desc_lower for keyword in system_keywords):
            return "system"
        
        # 数据处理类
        data_keywords = ["data", "分析", "处理", "解析", "akshare", "tushare"]
        if any(keyword in skill_name_lower or keyword in desc_lower for keyword in data_keywords):
            return "data"
        
        # AI类
        ai_keywords = ["ai", "模型", "智能", "learning", "deepseek", "kimi"]
        if any(keyword in skill_name_lower or keyword in desc_lower for keyword in ai_keywords):
            return "ai"
        
        # 默认返回system
        return "system"
    
    def _update_statistics(self):
        """更新统计信息"""
        registry = self.registry["registry"]
        
        total = len(registry)
        by_category = {cat: 0 for cat in self.registry["categories"]}
        active = 0
        inactive = 0
        
        for skill_id, skill_info in registry.items():
            category = skill_info.get("category", "system")
            if category in by_category:
                by_category[category] += 1
            
            if skill_info.get("status") == "active":
                active += 1
            else:
                inactive += 1
        
        self.registry["statistics"] = {
            "total_skills": total,
            "by_category": by_category,
            "active_skills": active,
            "inactive_skills": inactive
        }
    
    def find_skill(self, query: str, category: str = None) -> List[Dict]:
        """查找skill"""
        results = []
        query_lower = query.lower()
        
        for skill_id, skill_info in self.registry["registry"].items():
            # 检查分类
            if category and skill_info.get("category") != category:
                continue
            
            # 检查名称和描述
            name_match = query_lower in skill_info.get("name", "").lower()
            desc_match = query_lower in skill_info.get("description", "").lower()
            tag_match = any(query_lower in tag.lower() for tag in skill_info.get("tags", []))
            
            if name_match or desc_match or tag_match:
                results.append({
                    "id": skill_id,
                    **skill_info
                })
        
        # 按使用次数排序
        results.sort(key=lambda x: x.get("usage_count", 0), reverse=True)
        return results
    
    def get_skill(self, skill_id: str) -> Optional[Dict]:
        """获取指定skill的详细信息"""
        return self.registry["registry"].get(skill_id)
    
    def register_skill(self, skill_info: Dict) -> bool:
        """注册新的skill"""
        skill_id = skill_info.get("id")
        if not skill_id:
            print("Error: skill必须包含id")
            return False
        
        if skill_id in self.registry["registry"]:
            print(f"Warning: skill {skill_id} 已存在，将更新")
        
        self.registry["registry"][skill_id] = skill_info
        self._update_statistics()
        return self.save_registry()
    
    def update_skill_usage(self, skill_id: str):
        """更新skill使用次数"""
        if skill_id in self.registry["registry"]:
            skill_info = self.registry["registry"][skill_id]
            skill_info["usage_count"] = skill_info.get("usage_count", 0) + 1
            skill_info["last_used"] = datetime.now().isoformat()
            self.save_registry()
            return True
        return False
    
    def list_skills(self, category: str = None, source: str = None) -> List[Dict]:
        """列出所有skill"""
        results = []
        
        for skill_id, skill_info in self.registry["registry"].items():
            # 过滤条件
            if category and skill_info.get("category") != category:
                continue
            if source and skill_info.get("source") != source:
                continue
            
            results.append({
                "id": skill_id,
                "name": skill_info.get("name"),
                "description": skill_info.get("description", "")[:100] + "...",
                "category": skill_info.get("category"),
                "source": skill_info.get("source"),
                "usage_count": skill_info.get("usage_count", 0),
                "status": skill_info.get("status", "active")
            })
        
        # 按使用次数排序
        results.sort(key=lambda x: x.get("usage_count", 0), reverse=True)
        return results
    
    def generate_report(self) -> str:
        """生成注册表报告"""
        stats = self.registry["statistics"]
        
        report = f"""
# Skill注册表报告
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 统计概览
- 总skill数: {stats['total_skills']}
- 活跃skill: {stats['active_skills']}
- 非活跃skill: {stats['inactive_skills']}

## 分类统计
"""
        for category, count in stats["by_category"].items():
            if count > 0:
                category_name = self.registry["categories"].get(category, category)
                report += f"- {category_name}: {count}个\n"
        
        # 最常用skill
        report += "\n## 最常用skill (前10)\n"
        all_skills = []
        for skill_id, skill_info in self.registry["registry"].items():
            all_skills.append({
                "id": skill_id,
                "name": skill_info.get("name"),
                "usage_count": skill_info.get("usage_count", 0),
                "last_used": skill_info.get("last_used")
            })
        
        all_skills.sort(key=lambda x: x.get("usage_count", 0), reverse=True)
        for i, skill in enumerate(all_skills[:10], 1):
            last_used = skill.get("last_used", "从未使用")
            report += f"{i}. {skill['name']} - 使用次数: {skill['usage_count']} - 最后使用: {last_used}\n"
        
        return report

def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Skill注册表管理器")
    parser.add_argument("action", choices=["scan", "list", "find", "report", "register"],
                       help="执行的操作")
    parser.add_argument("--query", help="查找关键词")
    parser.add_argument("--category", help="分类过滤")
    parser.add_argument("--source", help="来源过滤 (user/system)")
    parser.add_argument("--force", action="store_true", help="强制重新扫描")
    
    args = parser.parse_args()
    
    registry = SkillRegistry()
    
    if args.action == "scan":
        registry.scan_skills(force_rescan=args.force)
    
    elif args.action == "list":
        skills = registry.list_skills(category=args.category, source=args.source)
        print(f"\n找到 {len(skills)} 个skill:\n")
        for skill in skills:
            print(f"{skill['id']}")
            print(f"  名称: {skill['name']}")
            print(f"  描述: {skill['description']}")
            print(f"  分类: {skill['category']} | 来源: {skill['source']}")
            print(f"  使用次数: {skill['usage_count']} | 状态: {skill['status']}")
            print()
    
    elif args.action == "find":
        if not args.query:
            print("Error: 需要提供查询关键词")
            return
        
        skills = registry.find_skill(args.query, args.category)
        print(f"\n找到 {len(skills)} 个匹配的skill:\n")
        for skill in skills:
            print(f"{skill['id']}")
            print(f"  名称: {skill['name']}")
            print(f"  描述: {skill['description'][:150]}...")
            print(f"  分类: {skill['category']} | 来源: {skill['source']}")
            print(f"  位置: {skill['location']}")
            print()
    
    elif args.action == "report":
        report = registry.generate_report()
        print(report)
        
        # 保存报告到文件
        report_path = os.path.join(registry.workspace, "skill_registry_report.md")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\n报告已保存到: {report_path}")
    
    elif args.action == "register":
        # 这里可以扩展为从文件注册
        print("注册功能待实现，请使用scan自动扫描")

if __name__ == "__main__":
    main()