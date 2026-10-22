# NIPS 2017 dev set: EDA numbers

- Images: 1000; sizes: {(299, 299): 1000}; modes: {'RGB': 1000}
- TrueLabel range: 2-996 (1001-class convention; class = TrueLabel - 1)
- Distinct classes: 430 of 1000; max images per class: 5; classes with exactly 1 image: 207
- Images per class distribution: {1: 207, 2: 71, 3: 37, 4: 35, 5: 80}
- Coarse groups (dataset share vs label-space share): Dog breeds: 1.1% vs 11.8%; Other animals: 19.3% vs 28.0%; Objects, scenes, food: 79.6% vs 60.2%
- Distinct target classes (TargetClass column): 604
- Channel mean (RGB): [0.473, 0.453, 0.41] vs ImageNet [0.485, 0.456, 0.406]
- Channel std (RGB): [0.279, 0.27, 0.286] vs ImageNet [0.229, 0.224, 0.225]
- Exact duplicate images: 0
- Saturated channel values (exactly 0 or 255): 2.5%
- Flickr-sourced: 100.0%; licenses: {'https://creativecommons.org/licenses/by/2.0/': 1000}
- Most frequent classes: buckeye (5), thatch (5), grocery store (5), Loafer (5), menu (5), cannon (5), mountain tent (5), carousel (5)
