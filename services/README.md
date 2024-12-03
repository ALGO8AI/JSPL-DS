# 1. digital-checklisting-app

## Route '/calculate-preparation-time'

input : {
  "delays": [
    {"Machine breakdown": 15},
    {"Material shortage": 20},
    {"Quality inspection": 10}
  ],
  "Mainteinence": [
    {"Electrode change": 15},
    {"Gunning": 20},
    {"Other": 10}
  ]
}

output: {
  "total preparation time": 45
}
