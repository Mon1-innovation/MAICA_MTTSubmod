init 980 python:
    @store.mas_submod_utils.functionplugin("ch30_preloop", priority=0)
    def mtts_migration():
        def migration_0_1_10():
            if renpy.seen_label("mtts_greeting"):
                persistent._seen_ever.update({"mtts_greeting_end":True})
        
        def m_1_0_4():
            try:
                os.remove(os.path.join(renpy.config.basedir, "game", "python-packages", "mtts.py"))
            except:
                pass

        import migrations
        migration = migrations.migration_instance(persistent._mtts_last_version, store.mtts_version)
        migration.migration_queue = [
            ("0.1.10", migration_0_1_10),
            ("1.0.4", m_1_0_4)
        ]
        migration.migrate()
        persistent._mtts_last_version = store.mtts_version
