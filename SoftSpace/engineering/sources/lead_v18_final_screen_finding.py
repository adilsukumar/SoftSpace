from pathlib import Path
P=Path(__file__).parent;f=P/'documents/build_documents.py';s=f.read_text()
needle="Native editable Fusion archives remain V10. No manufacturing release is claimed.')"
assert needle in s;s=s.replace(needle,needle+"\n  if (P/'engineering-v18-results'/'final_available_data_screen.json').exists():para(d,'The final holding screen finds a limited margin: the proposed minimum hinge torque is exhausted at about 1.15 g of equivalent static acceleration in the worst assumed mass case. Handling retention is not established. The final chapters record the material, clearance and saved CAD measurements and the inputs still needed.')",1)
needle="The final chapters explain the shared update.')"
assert needle in s;s=s.replace(needle,needle+"\n if (P/'engineering-v18-results'/'final_available_data_screen.json').exists():para(d,'The final standalone holding screen identifies a limited torque margin under assumed handling loads. This adds no measured Sony cushion benefit. The last chapters record the finding and the available data screening decision.')",1)
f.write_text(s)
