template = """[Unit]
Description=Synspark-logger Service
Documentation=man:synspark-logger(1)

[Service]
ExecStart=%(bin_path)s
Restart=always

[Install]
WantedBy=multi-user.target"""