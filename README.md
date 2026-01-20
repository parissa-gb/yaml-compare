# yaml-compare

> 🤖 **Note:** This tool was AI-generated and modified by the author.

A semantic YAML/ConfigMap comparison tool that generates interactive HTML reports with theme support.

---

## ✨ Features

- Semantic comparison (ignores formatting differences)
- Kubernetes ConfigMaps & Helm template support
- Nested key navigation via dot notation
- Interactive HTML reports with 3 themes (Light / Night / High Contrast)
- Collapsible sections with numbered items

---

## 📦 Dependencies
```bash
pip install pyyaml deepdiff
```

---

## 🚀 Usage
```bash
python3 yaml-compare.py <file1> <file2> <config_key1>:<config_key2> [start_key] [--html output.html]
```

### Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `file1` | ✅ | First YAML file |
| `file2` | ✅ | Second YAML file |
| `config_key` | ❌ | ConfigMap key (use `key1:key2` for different keys) |
| `start_key` | ❌ | Dot-notation path (e.g., `app.db.settings`) |
| `--html FILE` | ❌ | Generate HTML report |

---

## 📖 Examples

**Basic:**
```bash
python3 yaml-compare.py dev.yaml prod.yaml
```

**With ConfigMap key:**
```bash
python3 yaml-compare.py dev.yaml prod.yaml my-config
```

**Different keys per file:**
```bash
python3 yaml-compare.py dev.yaml prod.yaml config-dev:config-prod
```

**Nested path:**
```bash
python3 yaml-compare.py dev.yaml prod.yaml my-config app.database
```

**HTML report:**
```bash
python3 yaml-compare.py dev.yaml prod.yaml --html report.html
```

---

## 📤 Output

| Type | Description |
|------|-------------|
| **Console** | Formatted table with numbered differences |
| **HTML** | Interactive report with summary cards, collapsible sections, theme switcher |

<img width="1235" height="1234" alt="image" src="https://github.com/user-attachments/assets/fcf00009-626e-497e-af44-75057253fb22" />

