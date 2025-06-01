Para utilizar, entre na pasta "clips_processing" e rode "process_clip.py" e o caminho do clipe. 

Ex:
cd clips_processing
python .\save_frames.py .\clips\clip.mkv

---

Processa os clipes (process_clips.py), filtrando de acordo com movimento entre frames (movement_diff.py).
Ranges relevantes nos dados de movimento são salvos (process_ranges.py) e manualmente validados (validate_ranges.py).
Quando forem todos validados, os frames são salvos (save_frames.py).

--

Hiperparametros e outras opções em options.json.

Processamento:
"skip_frames": Quantidade de frames pulados ao gerar a diferença entre cada frame para análise.
"high_threshold" e "low_threshold": Ranges de moviemtno considerados válidos (normalizados de acordo com área do crop).
"window_size": Tamanho da janela usada para checar pontos de mudança nos dados de movimento.
"change_point_threshold": Porcentagem a se considerar como ponto de mudança (média da janela vs valor atual).

Plot:
"jump_seconds": Define o intervalo de ticks em segundos no plot.
"y_limit": Limite vertical do plot.

Save:
"skip_frames_save": Quantidade de frames pulados para gerar os frames finais.