def check_all_prices():
    history = load_history()
    updated_history = {}
    
    # 拼接一个总览通知，或者每次运行都强制发一条最新状态
    success_count = 0
    for item in TARGETS:
        item_id = item["id"]
        name = item["name"]
        url = item["url"]
        default_price = item["default_price"]
        
        fetched_price = fetch_real_price(url)
        last_record = history.get(item_id) or history.get(name) or {}
        current_price = fetched_price if fetched_price is not None else last_record.get("price", default_price)
        old_price = last_record.get("price", current_price)
        
        if fetched_price is not None:
            success_count += 1
            
        updated_history[item_id] = {
            "name": name,
            "price": current_price,
            "old_price": old_price,
            "drop_amount": round(old_price - current_price, 2) if current_price < old_price else 0.0,
            "drop_percent": round(((old_price - current_price) / old_price) * 100, 1) if current_price < old_price else 0.0,
            "update_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "product_url": url
        }
        
    save_history(updated_history)
    
    # 🔥 核心修改：每次脚本跑完，强制给手机发一条“最新抓取状态”通知！
    title = "📊 【MY 价格监控】最新抓取完成"
    body = f"云端已完成所有商铺巡检！成功抓取 {success_count}/{len(TARGETS)} 个商品最新价，Netlify 看板已同步更新。"
    print(body)
    send_bark_notification(title, body, url=NETLIFY_URL)
