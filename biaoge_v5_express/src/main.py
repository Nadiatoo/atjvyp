            print(f"\n⚠️ 风险评估:")
            print(f"   风险等级: {risk_assessment.get('risk_level', '中')}")
            print(f"   置信度: {risk_assessment.get('confidence', 0):.1f}")
            
            warnings = risk_assessment.get("warnings", [])
            if warnings:
                print(f"\n🚨 风险警告:")
                for warning in warnings:
                    print(f"   • {warning}")
            
            actions = risk_assessment.get("suggested_actions", [])
            if actions:
                print(f"\n✅ 建议行动:")
                for action in actions:
                    print(f"   • {action}")
            
            print("\n" + "="*60)
            print("📝 报告生成完成")
            print("="*60 + "\n")
            
        except Exception as e:
            logger.error(f"输出分析报告失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        logger.info("清理系统资源")
        self.data_manager.cleanup_all()
        logger.info("系统资源清理完成")


def main():
    """主函数"""
    try:
        logger.info("启动彪哥战法v5.0系统")
        
        # 创建系统实例
        system = BiaogeStrategyV5()
        
        # 运行每日分析
        report = system.run_daily_analysis()
        
        if report:
            logger.info("每日分析成功完成")
        else:
            logger.warning("每日分析完成，但可能存在问题")
        
        # 清理资源
        system.cleanup()
        
        logger.info("彪哥战法v5.0系统运行完成")
        
    except KeyboardInterrupt:
        logger.info("用户中断程序")
    except Exception as e:
        logger.error(f"系统运行失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()