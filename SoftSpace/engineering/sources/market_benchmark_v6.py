"""Documented sample, not an exhaustive market census or tested ranking."""
import csv,json
from pathlib import Path
p=Path(__file__).parent/'engineering-v6-results';p.mkdir(exist_ok=True)
rows=[]
def add(product,category,feature,weight,price,availability,url):
 rows.append(dict(product=product,category=category,manufacturer_feature=feature,manufacturer_mass_g=weight,price_observation=price,india_availability=availability,source=url,checked_date='2026-10-13',comfort_comparison='Unknown; no matched wearer test',attenuation_comparison='Unknown; no matched acoustic test'))
add('Robustt adjustable earmuffs','Passive defender','Adjustable headband; soft foam; manufacturer claims NRR21 (test report not reviewed)','','INR808 pack of2; INR404/unit before delivery','Indian direct listing; delivery/stock not verified','https://www.robustt.in/products/earmuffs-for-noise-reduction-red-and-black')
add('SYGA EM39 children earmuffs','Passive defender','Child product; adjustable padding','','INR699 listing','Indian listing; conflicting inventory messages','https://syga.in/products/1001106')
add('Pax Parrot children earmuffs','Passive defender','Adjustable child ear defenders','','INR299 sale listing','Indian direct listing; stock not verified','https://paxparrot.com/products/noise-cancellation-earmuffs-for-kids-1')
add('3M Peltor X4A','Passive defender','Manufacturer UK SNR33; distinct from US NRR27','','INR4435 Flipkart listing / INR10833.73 element14 listing','Retail quote; PIN delivery unverified; element14 imports UK stock','https://www.3m.co.uk/3M/en_GB/p/d/v000137013/')
add('Alpine Muffy Kids','Passive defender','Adjustable ages5–16; advertised25dB; maker warns glasses can affect seal','174','USD29.95 foreign store','Indian import listing found; delivered cost unverified','https://www.alpinehearingprotection.com/products/muffy-kids')
add('Alpine Defender','Passive defender','Advertised26dB passive defender','249','','India availability unverified','https://www.alpinehearingprotection.com/products/alpine-defender?variant=44017496326363')
add('Banz Kids','Passive defender','Child passive earmuffs','190','GBP19.95 foreign store','India availability unverified','https://europe.babybanz.com/products/earbanz-kids-hearing-protection?variant=12410019610696')
add('Noisefighters Sightlines','Replacement cushion','Gel plus memory foam; glasses relief cuts; adapter compatibility','','USD60 before shipping/import costs','No verified Indian stock in this search; not proof none exists','https://noisefighters.com/collections/hearing/products/sightlines1')
add('Turtle Beach ProSpecs system','Glasses relief system','Adjustable relief channels/cuts; Elite Pro tab controls cushion depth','','','Exact India model/price unverified','https://uk.turtlebeach.com/blog/memory-foam-ear-cushions-prospecs-glasses-gamers')
add('Turtle Beach Stealth600','Gaming headset','Glasses-friendly memory foam and athletic-weave cushions','','','India delivered price unverified','https://www.turtlebeach.com/products/stealth-600-headset?Color=Purple&Platform=Xbox')
add('Brainwavz oval pad range','Replacement cushion','Oval, hybrid/velour and cooling-gel options; model fit guide','','','Indian price/stock and model fit require checking','https://www.brainwavzaudio.com/pages/brainwavz-earpad-guide')
add('Wicked Cushions WC Freeze','Replacement cushion','Cooling gel gaming cushions; model-specific fit','','','India delivered price unverified','https://wickedcushions.com/products/wc-freeze-cooling-gel-gaming-ear-cushions?variant=39299092807759')
add('Sony WH-CH720N','ANC audio headset','Electronic ANC','192','','Sony India documentation; retail stock unverified','https://www.sony.co.in/electronics/support/wireless-headphones-bluetooth-headphones/wh-ch720n/specifications')
add('Sony WH-1000XM5','ANC audio headset','Electronic ANC','','','Sony India documentation; retail stock unverified','https://www.sony.co.in/electronics/headband-headphones/wh-1000xm5/specifications')
add('Sony WH-1000XM6','ANC audio headset','Electronic ANC','254','','Sony India documentation; retail stock unverified','https://www.sony.co.in/electronics/support/wireless-headphones-bluetooth-headphones/wh-1000xm6/specifications')
add('JBL Tune770NC','ANC audio headset','ANC; specified ear opening54x37mm','232','','India delivered price unverified','https://www.jbl.com/TUNE770NC.html?dwvar_TUNE770NC_color=White-AM-Current&locale=en_US')
add('JBL Live770NC','ANC audio headset','Electronic ANC','255','','India delivered price unverified','https://www.jbl.com/on/demandware.static/-/Sites-masterCatalog_Harman/default/dwaf75a2d8/pdfs/JBL_LIVE%20770NC_QSG_Multilingual.pdf')
add('JBL TourOneM3','ANC audio headset','Electronic ANC','278','','India delivered price unverified','https://uk.jbl.com/TOUR-ONE-M3.html?dwvar_TOUR-ONE-M3_color=Black-EMEA-Current')
add('Bose QuietComfort Ultra2ndGen','ANC audio headset','Electronic ANC','','','India delivered price unverified','https://www.bose.co.uk/p/headphones/bose-quietcomfort-ultra-headphones-2nd-gen/QCUH2-HEADPHONEARN.html?dwvar_QCUH2-HEADPHONEARN_color=CHERRY+CHOCOLATE&quantity=1')
add('Bose QuietComfort2ndGen','ANC audio headset','Electronic ANC','','','India delivered price unverified','https://www.bose.com/p/headphones/bose-quietcomfort-headphones-2nd-gen/QC2G-HEADPHONEARN.html?dwvar_QC2G-HEADPHONEARN_color=WHITE+SMOKE')
add('Sennheiser Momentum4','ANC audio headset','Electronic ANC; official manual','','','India delivered price unverified','https://cdn.sennheiser-hearing.com/product-documents/product-downloads/momentum-4-wireless/Instruction%20manual%20MOMENTUM%204%20Wireless/Instruction_manual_MOMENTUM_4_Wireless.pdf')
add('Sennheiser AccentumPlus','ANC audio headset','Electronic ANC; official manual','','','India delivered price unverified','https://cdn.sennheiser-hearing.com/product-documents/product-downloads/accentum-plus-wireless/Instruction%20manual%20ACCENTUM%20Plus/Instruction_manual_ACCENTUM_Plus.pdf')
add('Soundcore SpaceQ45','ANC audio headset','Electronic ANC','','','India delivered price unverified','https://www.soundcore.com/products/space-q45-a3040011')
add('Soundcore SpaceOne','ANC audio headset','Electronic ANC','','','India delivered price unverified','https://www.soundcore.com/products/space-one-a3035011?variant=44247740022974')
add('Soundcore Q20i','ANC audio headset','Electronic ANC','','','India delivered price unverified','https://us.soundcore.com/products/q20i-a3004z31?variant=46396740796606')
add('boAt Nirvana751ANC','ANC audio headset','Electronic ANC','','INR5099 displayed; INR3099 conditional FESTIVE2000 coupon','Indian direct site says restocking soon; stock not confirmed','https://www.boat-lifestyle.com/products/nirvana-751-anc-headphone')
add('Beats StudioPro','ANC audio headset','Electronic ANC','260','','India delivered price unverified','https://www.beatsbydre.com/headphones/studio-pro-wireless?pp=1')
add('Razer BlackSharkV2Pro2023','Gaming headset','Breathable memory-foam cushions','','','India delivered price unverified','https://mysupport.razer.com/app/answers/detail/a_id/13060/~/razer-blackshark-v2-pro-%282023%29-%7C-rz04-0453-support-%26-faqs')
add('HyperX CloudIII','Gaming headset','Memory foam and leatherette cushions','','','India delivered price unverified','https://uk.hyperx.com/collections/cloud-iii/products/hyperx-cloud-iii-wired-gaming-headset?variant=42487387259036')
(p/'market_sample.json').write_text(json.dumps(rows,indent=2))
with (p/'market_sample.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
text='''# Indian affordability and market comparison

This is a documented sample of %d products/ranges, not every headphone on sale. No matched acoustic or wearer experiments were performed on competitors. Manufacturer feature claims are separated from our own simulations. Blank mass/price fields mean unverified, not zero. Listed foreign prices exclude delivery/import charges; listing presence does not confirm Indian availability.

Our primary objective remains an affordable passive defender designed with autistic users. Local service, fit options, low noise from handling, tolerable textures and an affordable purchase price are possible differentiators. They remain product hypotheses. The design does not yet outperform any comparator on measured comfort, attenuation, sensory acceptance, durability or cost.

Cheap passive defenders already have Indian listings, including Robustt at INR808 per two (INR404 per unit) and child products from SYGA/Pax Parrot. We cannot claim the cheapest product without a bill of materials and manufacturing quotes. These listings do not establish that their comfort is suitable for autistic users.

Turtle Beach ProSpecs includes engineered, adjustable glasses relief channels; it is more than ordinary memory foam. Noisefighters Sightlines combines gel, foam and glasses relief cuts. Its USD60 foreign price and unverified Indian stock leave a possible affordability/access gap, but do not establish that no alternative exists in India.

Replacement cushions must fit specific mounting interfaces. A shared comfort design can be adapted into model-specific carriers; one pad cannot be claimed compatible with all brands. Existing headband force, cup geometry and pad mounting still affect pressure, seal and sound, so compatibility testing remains necessary even though we do not design the customer's headband.

Our adult pad opening is50x70mm, child42.5x59.5mm. The documented JBL Tune770NC opening is54x37mm. A larger opening alone does not prove better fit. Our estimated child mass is132–197g and adult168–252g, depending on assumed densities. These CAD estimates overlap reported competitor masses; no universal weight advantage is established.

NRR, SNR, ANC marketing numbers and model pressure-transfer dB are different quantities. They cannot form a valid ranking. An audio ANC headset and a passive sensory defender also serve different functions. The intended defender requires no powered electronics or generated white noise; internal handling noise and wearer acceptance still need assessment.

Some autistic people find external sounds distressing; needs vary between people and environments. Noise-reduction headphones have limited supportive evidence, including a small study of six children, but that study did not test our design: https://www.frontiersin.org/journals/integrative-neuroscience/articles/10.3389/fnint.2019.00065/full

Source-linked rows follow in market_sample.csv and market_sample.json. Retail context for 3M quotes: https://www.flipkart.com/3m-x4a-peltor-x-series-1n-ear-muff/p/itmfhz88hfxqk9rx and https://in.element14.com/3m/x4a/ear-defender-headband-muff-8khz/dp/2675823
'''%len(rows)
(p/'MARKET.md').write_text(text,encoding='utf-8');print('Saved',len(rows),'documented market entries')
