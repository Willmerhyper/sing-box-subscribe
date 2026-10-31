# 操作说明去看[英文文档](https://github.com/Toperlock/sing-box-subscribe/blob/main/instructions/README.md)，中文文档操作说明不再提供

# 免责声明：sing-box-subscribe.vercel.app域名目前已被其他人占用，与本项目无关。后果自负
![image](https://github.com/Toperlock/sing-box-subscribe/assets/86833913/f9af80bc-f1b7-45dd-a2eb-e26910069f21)

### 使用 `/config/URL` 添加参数符号已修改，从原来的 `/&` 改为 `&`。有问题请提issue，不要打扰 `sing-box`

```
https://xxxxxxx.vercel.app/config/https://xxxxxxsubscribe?token=123456&file=https://github.com/Toperlock/sing-box-subscribe/raw/main/config_template/config_template_groups_rule_set_tun.json
```

```
https://xxxxxxx.vercel.app/config/https://xxxxxxsubscribe?token=123456&file=2
```

本地python执行脚本命令：

```
python main.py
```

或者你可以直接带template_index参数选定模板，0表示第一个模板(no flask不支持此参数)

```
python main.py --template_index=0
```

支持Docker

```
docker build --tag 'sing-box' .
docker run -p 5000:5000 sing-box:latest
```

支持自定义GitHub加速链接（使用参数&gh=1 数字代表使用第一个github加速），默认不加此参数。只有原始GitHub文件链接或者已经使用以下GitHub加速链接才能替换

```
1. "https://gh-proxy.com/",
2. "https://gh.sageer.me/",
3. "https://ghproxy.com/",
4. "https://mirror.ghproxy.com/",
5. "https://cdn.jsdelivr.net",
6. "https://testingcf.jsdelivr.net"
```

### 根据已有的qx，surge，loon，clash规则列表自定义规则集[https://github.com/Toperlock/sing-box-geosite](https://github.com/Toperlock/sing-box-geosite)

### wechat规则集源文件写法：
```json
{
  "version": 1,
  "rules": [
    {
      "domain": [
        "dl.wechat.com",
        "sgfindershort.wechat.com",
        "sgilinkshort.wechat.com",
        "sglong.wechat.com",
        "sgminorshort.wechat.com",
        "sgquic.wechat.com",
        "sgshort.wechat.com",
        "tencentmap.wechat.com.com",
        "qlogo.cn",
        "qpic.cn",
        "servicewechat.com",
        "tenpay.com",
        "wechat.com",
        "wechatlegal.net",
        "wechatpay.com",
        "weixin.com",
        "weixin.qq.com",
        "weixinbridge.com",
        "weixinsxy.com",
        "wxapp.tc.qq.com"
      ]
    },
    {
      "domain_suffix": [
        ".qlogo.cn",
        ".qpic.cn",
        ".servicewechat.com",
        ".tenpay.com",
        ".wechat.com",
        ".wechatlegal.net",
        ".wechatpay.com",
        ".weixin.com",
        ".weixin.qq.com",
        ".weixinbridge.com",
        ".weixinsxy.com",
        ".wxapp.tc.qq.com"
      ]
    },
    {
      "ip_cidr": [
        "101.32.104.4/32",
        "101.32.104.41/32",
        "101.32.104.56/32",
        "101.32.118.25/32",
        "101.32.133.16/32",
        "101.32.133.209/32",
        "101.32.133.53/32",
        "129.226.107.244/32",
        "129.226.3.47/32",
        "162.62.163.63/32"
      ]
    }
  ]
}
```
配置文件添加源文件规则集：
```
{
  "tag": "geosite-wechat",
  "type": "remote",
  "format": "source",
  "url": "https://raw.githubusercontent.com/Toperlock/sing-box-geosite/main/wechat.json",
  "download_detour": "auto"
}
```



## Hyperchem — macOS 官方 sing-box 1.14

自用模板：`config_template/hyperchem-1.14.json`。

通过自己的 Vercel 转换器使用远程模板，客户端每次更新配置时会重新读取订阅并合并最新模板：

```text
https://singbox.hyperchem.top/config/<URL编码后的订阅源>&file=<URL编码后的模板链接>&ua=Shadowrocket
```

模板链接为 `https://raw.githubusercontent.com/Willmerhyper/sing-box-subscribe/main/config_template/hyperchem-1.14.json`。订阅源与模板链接均用 `encodeURIComponent` / `urllib.parse.quote(value, safe="")` 编码，避免 Vercel 对路径中的双斜线重定向。

- TUN + 本机 `127.0.0.1:7890` mixed 入站，提供 macOS 系统 HTTP 代理。
- `Proxy` 手动选节点，默认 `Auto` 自动测速；`Anthropic` 与 `OpenAI` 有独立选择分组。
- Anthropic、OpenAI、Telegram、YouTube、Twitter、Facebook、Netflix、TikTok、Microsoft、AppleMusic、Bilibili 和 WeChat 使用自己的 `Willmerhyper/sing-box-geosite` 仓库规则。
- 国内域名基础分流补充使用 MetaCubeX `cn.srs`；国内和局域网直连，其他流量默认代理。
- 分类型 DNS，国内使用直连 DoH，海外使用经代理的 DoH；节点域名通过独立 bootstrap DNS 解析，避免解析循环。
- 使用 1.14 的显式 HTTP client 下载规则；未使用旧 DNS server 格式、旧 DNS/block 出站或旧入站 sniff 字段。
- 模板只包含公共规则与分组；不要把私人订阅、节点密码或最终含节点的配置提交到仓库。
- 将转换后的链接作为 macOS 官方客户端远程配置导入；下载 JSON 仅为静态快照。规则集每 1 天更新，节点更新由客户端的远程配置更新触发。


### 自用模板节点精简

`hyperchem-1.14.json` 的 `_node_selection` 是转换器指令，生成配置时会删除，不传给 sing-box。
按订阅中的原始顺序保留前 2 个 Hong Kong、前 2 个 Japan、USA Seattle 01 和全部 USA Los Angeles。
该筛选在分组展开之前执行，未选中的节点也不会进入最终 `outbounds`；不限洛杉矶节点数量，以便订阅新增同城节点时自动纳入。
