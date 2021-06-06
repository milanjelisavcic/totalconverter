# Temis AI

**Temis** uses AI to accomplish what was previously impossible with other methods: helping legal and compliance teams make their work more efficient as they face a large number of regulations and business expectations in the digital banking environment. Along with a network of domain experts in legal, we harness the power of AI to identify patterns in cross-border rules data.

## Installation

The system use Python Flask as the core framework.
Installation is straightforward.
First, clone the project:

```bash
git clone https://github.com/Temis-AI/temis-core.git
cd temis-core/
```

Within the `temis-core/` root directory create Python virtual environment:

```bash
conda create -n temis python=3.7.10
conda activate temis
conda install -r requirements.txt
```

Finally, run the application:

```bash
flask run
```

To verify the installation, the application home screen is visible on URI https://localhost:5000/

## Contribution guidelines

If you want to contribute to Revolve, be sure to review the [contribution
guidelines](CONTRIBUTING.md). By participating, you are expected to
uphold this code.

We use [GitHub issues](https://github.com/Temis-AI/temis-core/issues) for
tracking requests and bugs.

## For more information

* [Temis AI](https://temis.ai/)
* [API documentation](https://temisai.docs.apiary.io/)
