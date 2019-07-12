# Docker for API

You can build and run the docker using the following process:

Cloning
```console
git clone https://github.com/jqueguiner/Deep-Photo-Enhancement.git
```

Building Docker
```console
cd Deep-Photo-Enhancement && docker build -t Deep-Photo-Enhancement -f Dockerfile .
```

Running Docker
```console
echo "http://$(curl ifconfig.io):5000" && docker run -p 5000:5000 -d Deep-Photo-Enhancement
```

Calling the API
```console
curl -X POST "http://MY_SUPER_API_IP:5000/process" -H "accept: image/*" -H "Content-Type: application/json" -d '{"url": "https://i.stack.imgur.com/aeY45.jpg", "phone": "iphone", "resolution":"orig"}'
```
