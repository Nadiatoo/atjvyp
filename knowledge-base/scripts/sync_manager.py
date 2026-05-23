#!/usr/bin/env python3
"""
同步管理器 - 同步文件系统和向量数据库
"""

import time
from datetime import datetime
from typing import Dict, List, Any
import json

from file_monitor import FileMonitor
from vector_db import VectorDatabase

class SyncManager:
    """同步管理器"""
    
    def __init__(self, config_dir: str = None):
        """初始化同步管理器"""
        print("🔄 初始化同步管理器...")
        
        # 初始化组件
        self.file_monitor = FileMonitor()
        self.vector_db = VectorDatabase(config_dir)
        
        # 同步状态
        self.sync_state_file = self.file_monitor.base_dir.parent / "vectors" / "metadata" / "sync_state.json"
        self.sync_state_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.sync_state = self._load_sync_state()
        
        print("✅ 同步管理器初始化完成")
    
    def _load_sync_state(self) -> Dict[str, Any]:
        """加载同步状态"""
        if self.sync_state_file.exists():
            try:
                with open(self.sync_state_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ 加载同步状态失败: {e}")
                return {}
        else:
            return {
                "last_full_sync": None,
                "last_incremental_sync": None,
                "total_synced_files": 0,
                "sync_history": []
            }
    
    def _save_sync_state(self):
        """保存同步状态"""
        try:
            with open(self.sync_state_file, 'w', encoding='utf-8') as f:
                json.dump(self.sync_state, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"❌ 保存同步状态失败: {e}")
    
    def _record_sync_event(self, event_type: str, details: Dict[str, Any]):
        """记录同步事件"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details
        }
        
        self.sync_state["sync_history"].append(event)
        
        # 只保留最近100个事件
        if len(self.sync_state["sync_history"]) > 100:
            self.sync_state["sync_history"] = self.sync_state["sync_history"][-100:]
        
        self._save_sync_state()
    
    def incremental_sync(self) -> Dict[str, Any]:
        """增量同步：只处理变化的文件"""
        print("🔄 开始增量同步...")
        start_time = time.time()
        
        # 扫描文件变化
        added, modified, deleted = self.file_monitor.scan_files()
        
        sync_stats = {
            "added": len(added),
            "modified": len(modified),
            "deleted": len(deleted),
            "success": 0,
            "failed": 0
        }
        
        # 处理新增和修改的文件
        for file_list, change_type in [(added, "added"), (modified, "modified")]:
            for file_info in file_list:
                try:
                    # 获取文件内容
                    content = self.file_monitor.get_file_content(file_info["relative_path"])
                    
                    if not content:
                        print(f"⚠️  文件内容为空: {file_info['relative_path']}")
                        continue
                    
                    # 准备元数据
                    metadata = {
                        "file_path": file_info["file_path"],
                        "relative_path": file_info["relative_path"],
                        "domain": file_info["domain"],
                        "category": file_info["category"],
                        "tags": file_info["tags"],
                        "size": file_info["size"],
                        "timestamp": file_info["timestamp"],
                        "content_hash": file_info["content_hash"]
                    }
                    
                    # 更新向量数据库
                    # 注意：这里需要向量，我们先使用简单占位符
                    # 实际使用时需要调用嵌入模型
                    vector = None  # 这里应该是实际的向量
                    
                    doc_id = self.vector_db.update_document(
                        file_path=file_info["relative_path"],
                        content=content,
                        metadata=metadata,
                        vector=vector
                    )
                    
                    if doc_id:
                        sync_stats["success"] += 1
                        print(f"✅ {change_type}: {file_info['relative_path']}")
                    else:
                        sync_stats["failed"] += 1
                        print(f"❌ {change_type}失败: {file_info['relative_path']}")
                        
                except Exception as e:
                    sync_stats["failed"] += 1
                    print(f"❌ 处理文件失败 {file_info['relative_path']}: {e}")
        
        # 处理删除的文件
        for file_info in deleted:
            try:
                success = self.vector_db.delete_document(file_info["relative_path"])
                if success:
                    sync_stats["success"] += 1
                    print(f"🗑️  删除: {file_info['relative_path']}")
                else:
                    sync_stats["failed"] += 1
            except Exception as e:
                sync_stats["failed"] += 1
                print(f"❌ 删除文件失败 {file_info['relative_path']}: {e}")
        
        # 更新同步状态
        self.sync_state["last_incremental_sync"] = datetime.now().isoformat()
        self.sync_state["total_synced_files"] = self.vector_db.collection.count()
        
        elapsed_time = time.time() - start_time
        
        # 记录同步事件
        self._record_sync_event("incremental", {
            "stats": sync_stats,
            "elapsed_time": elapsed_time
        })
        
        print(f"✅ 增量同步完成")
        print(f"   耗时: {elapsed_time:.2f}秒")
        print(f"   新增: {sync_stats['added']}, 修改: {sync_stats['modified']}, 删除: {sync_stats['deleted']}")
        print(f"   成功: {sync_stats['success']}, 失败: {sync_stats['failed']}")
        
        return sync_stats
    
    def full_sync(self) -> Dict[str, Any]:
        """全量同步：重新处理所有文件"""
        print("🔄 开始全量同步...")
        start_time = time.time()
        
        # 获取所有文件
        all_files = self.file_monitor.get_all_files()
        
        sync_stats = {
            "total_files": len(all_files),
            "processed": 0,
            "success": 0,
            "failed": 0
        }
        
        # 清空向量数据库（可选）
        # 注意：这里需要谨慎，实际使用时可能需要备份
        print("⚠️  全量同步将重新处理所有文件...")
        
        for file_info in all_files:
            try:
                # 获取文件内容
                content = self.file_monitor.get_file_content(file_info["relative_path"])
                
                if not content:
                    print(f"⚠️  文件内容为空: {file_info['relative_path']}")
                    sync_stats["processed"] += 1
                    continue
                
                # 准备元数据
                metadata = {
                    "file_path": file_info["file_path"],
                    "relative_path": file_info["relative_path"],
                    "domain": file_info["domain"],
                    "category": file_info["category"],
                    "tags": file_info["tags"],
                    "size": file_info["size"],
                    "timestamp": file_info["timestamp"],
                    "content_hash": file_info["content_hash"]
                }
                
                # 更新向量数据库
                vector = None  # 这里应该是实际的向量
                
                doc_id = self.vector_db.update_document(
                    file_path=file_info["relative_path"],
                    content=content,
                    metadata=metadata,
                    vector=vector
                )
                
                if doc_id:
                    sync_stats["success"] += 1
                else:
                    sync_stats["failed"] += 1
                
                sync_stats["processed"] += 1
                
                # 进度显示
                if sync_stats["processed"] % 10 == 0:
                    print(f"📊 进度: {sync_stats['processed']}/{sync_stats['total_files']}")
                    
            except Exception as e:
                sync_stats["failed"] += 1
                sync_stats["processed"] += 1
                print(f"❌ 处理文件失败 {file_info['relative_path']}: {e}")
        
        # 更新同步状态
        self.sync_state["last_full_sync"] = datetime.now().isoformat()
        self.sync_state["last_incremental_sync"] = datetime.now().isoformat()
        self.sync_state["total_synced_files"] = self.vector_db.collection.count()
        
        elapsed_time = time.time() - start_time
        
        # 记录同步事件
        self._record_sync_event("full", {
            "stats": sync_stats,
            "elapsed_time": elapsed_time
        })
        
        print(f"✅ 全量同步完成")
        print(f"   耗时: {elapsed_time:.2f}秒")
        print(f"   总文件: {sync_stats['total_files']}")
        print(f"   成功: {sync_stats['success']}, 失败: {sync_stats['failed']}")
        
        return sync_stats
    
    def verify_sync(self) -> Dict[str, Any]:
        """验证同步一致性"""
        print("🔍 验证同步一致性...")
        
        # 获取文件系统中的文件
        file_system_files = self.file_monitor.get_all_files()
        file_system_count = len(file_system_files)
        
        # 获取向量数据库中的文件
        vector_db_stats = self.vector_db.get_stats()
        vector_db_count = vector_db_stats.get("document_count", 0)
        
        # 检查不一致的文件
        inconsistencies = []
        
        for file_info in file_system_files:
            # 检查文件是否在向量数据库中
            # 这里需要实际查询向量数据库
            # 暂时跳过详细检查
            
            # 简单检查：文件大小和哈希
            pass
        
        verification_result = {
            "file_system_count": file_system_count,
            "vector_db_count": vector_db_count,
            "count_match": file_system_count == vector_db_count,
            "inconsistencies_count": len(inconsistencies),
            "inconsistencies": inconsistencies[:10]  # 只显示前10个
        }
        
        print(f"📊 验证结果:")
        print(f"   文件系统: {verification_result['file_system_count']}个文件")
        print(f"   向量数据库: {verification_result['vector_db_count']}个文档")
        
        if verification_result["count_match"]:
            print("✅ 文件数量一致")
        else:
            print(f"⚠️  文件数量不一致，差异: {abs(file_system_count - vector_db_count)}")
        
        if verification_result["inconsistencies_count"] > 0:
            print(f"⚠️  发现 {verification_result['inconsistencies_count']} 个不一致")
        
        return verification_result
    
    def print_status(self):
        """打印同步状态"""
        print("=" * 50)
        print("同步管理器状态")
        print("=" * 50)
        
        # 文件系统状态
        added, modified, deleted = self.file_monitor.scan_files()
        print(f"📁 文件系统:")
        print(f"   总文件数: {len(self.file_monitor.file_states)}")
        print(f"   待处理: +{len(added)} ✏️{len(modified)} -{len(deleted)}")
        
        # 向量数据库状态
        vector_stats = self.vector_db.get_stats()
        print(f"📊 向量数据库:")
        print(f"   文档数量: {vector_stats.get('document_count', 0)}")
        print(f"   集合名称: {vector_stats.get('collection_name', 'N/A')}")
        
        # 同步状态
        print(f"🔄 同步状态:")
        print(f"   最后全量同步: {self.sync_state.get('last_full_sync', '从未')}")
        print(f"   最后增量同步: {self.sync_state.get('last_incremental_sync', '从未')}")
        print(f"   总同步文件: {self.sync_state.get('total_synced_files', 0)}")
        
        # 同步历史
        sync_history = self.sync_state.get("sync_history", [])
        if sync_history:
            print(f"📜 最近同步:")
            for event in sync_history[-3:]:  # 显示最近3次
                print(f"   • {event['timestamp']}: {event['type']}")
        
        print("=" * 50)

if __name__ == "__main__":
    # 测试同步管理器
    print("🧪 测试同步管理器...")
    
    sync_manager = SyncManager()
    sync_manager.print_status()
    
    # 运行增量同步
    print("\n运行增量同步...")
    sync_stats = sync_manager.incremental_sync()
    
    # 验证同步
    print("\n验证同步...")
    verification = sync_manager.verify_sync()
    
    # 打印最终状态
    print("\n最终状态:")
    sync_manager.print_status()
    
    print("✅ 同步管理器测试完成")