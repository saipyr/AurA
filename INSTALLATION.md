### Installing Both Ollama and AurA IDE Using Kustomize

For cpu-only pod

```bash
kubectl apply -f ./kubernetes/manifest/base
```

For gpu-enabled pod

```bash
kubectl apply -k ./kubernetes/manifest
```

### Installing Both Ollama and AurA IDE Using Helm

Package Helm file first

```bash
helm package ./kubernetes/helm/
```

For cpu-only pod

```bash
helm install ollama-aura ./ollama-aura-*.tgz
```

For gpu-enabled pod

```bash
helm install ollama-aura ./ollama-aura-*.tgz --set ollama.resources.limits.nvidia.com/gpu="1"
```

Check the `kubernetes/helm/values.yaml` file to know which parameters are available for customization
