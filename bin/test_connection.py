from futu import SysConfig, OpenQuoteContext

SysConfig.set_all_thread_daemon(True)
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)  # Create quote object
assert quote_ctx.get_sync_conn_id()
quote_ctx.close()

print("test connection pass")
