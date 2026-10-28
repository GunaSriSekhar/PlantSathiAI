# PlantSathi AI — Model Setup & Provenance Guide

## 1. Computer Vision Models

PlantSathi AI uses local, open-source model checkpoints from Hugging Face Hub. **No API keys or external subscriptions are required.**

### A. Plant Species Identification
* **Repository ID:** `umutbozdag/plant-identity`
* **Architecture:** Vision Transformer (ViT)
* **License:** Apache 2.0 / Open Source
* **Auto-Download:** On initial inference request, the model weights (~340MB) are automatically downloaded from Hugging Face Hub and cached locally.
* **Cache Directory:** `./model_cache/transformers`

### B. Plant Disease Classification
* **Repository ID:** `linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification`
* **Architecture:** MobileNetV2 (1.0 width multiplier, 224×224 input)
* **Dataset:** PlantVillage (54,305 images)
* **Size:** ~14MB (lightweight, runs efficiently on CPU and mobile devices)
* **License:** Apache 2.0

---

## 2. All 38 PlantVillage Classes

The disease classifier recognizes the exact following 38 classes:

1. `Apple___Apple_scab`
2. `Apple___Black_rot`
3. `Apple___Cedar_apple_rust`
4. `Apple___healthy`
5. `Blueberry___healthy`
6. `Cherry_(including_sour)___Powdery_mildew`
7. `Cherry_(including_sour)___healthy`
8. `Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot`
9. `Corn_(maize)___Common_rust_`
10. `Corn_(maize)___Northern_Leaf_Blight`
11. `Corn_(maize)___healthy`
12. `Grape___Black_rot`
13. `Grape___Esca_(Black_Measles)`
14. `Grape___Leaf_blight_(Isariopsis_Leaf_Spot)`
15. `Grape___healthy`
16. `Orange___Haunglongbing_(Citrus_greening)`
17. `Peach___Bacterial_spot`
18. `Peach___healthy`
19. `Pepper,_bell___Bacterial_spot`
20. `Pepper,_bell___healthy`
21. `Potato___Early_blight`
22. `Potato___Late_blight`
23. `Potato___healthy`
24. `Raspberry___healthy`
25. `Soybean___healthy`
26. `Squash___Powdery_mildew`
27. `Strawberry___Leaf_scorch`
28. `Strawberry___healthy`
29. `Tomato___Bacterial_spot`
30. `Tomato___Early_blight`
31. `Tomato___Late_blight`
32. `Tomato___Leaf_Mold`
33. `Tomato___Septoria_leaf_spot`
34. `Tomato___Spider_mites Two-spotted_spider_mite`
35. `Tomato___Target_Spot`
36. `Tomato___Tomato_Yellow_Leaf_Curl_Virus`
37. `Tomato___Tomato_mosaic_virus`
38. `Tomato___healthy`

---

## 3. Pre-Warming & Offline Execution

Once the weights are downloaded on first run, the platform functions **100% offline**. You can pre-download weights by running:

```powershell
python -c "from transformers import pipeline; pipeline('image-classification', model='linkanjarad/mobilenet_v2_1.0_224-plant-disease-identification')"
```
