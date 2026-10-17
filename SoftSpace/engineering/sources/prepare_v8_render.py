from pathlib import Path
p=Path(__file__).parent;s=(p/'render_cad_review.py').read_text().replace('engineering-v7-results','engineering-v8-results').replace('cad_v7_report','cad_v8_report').replace('V7 digital concept','V8 lower-crown digital concept')
(p/'render_v8_review.py').write_text(s)
