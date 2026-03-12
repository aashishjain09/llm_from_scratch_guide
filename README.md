# LLM from Scratch Guide + Multi-Agent Automation Showcase

A comprehensive educational project for building Large Language Models from first principles, combined with production-ready multi-agent automation systems showcasing enterprise operations optimization.

## 📚 Project Structure

This repository is organized into three main sections:

### 1. Core LLM Implementation (Educational Foundation)
The foundational LLM training codebase covering the complete pipeline from data preparation through fine-tuning:

- **[config/](config/)** - Centralized hyperparameter configuration
- **[src/](src/)** - Core transformer architecture
  - `models/transformer.py` - Complete transformer stack
  - `models/attention.py` - Multi-head self-attention with causal masking
  - `models/mlp.py` - Feed-forward networks
  - `models/transformer_block.py` - Transformer block architecture
- **[data_loader/](data_loader/)** - Efficient data loading from HDF5
- **[scripts/](scripts/)** - Training and inference pipelines
  - `data_download.py` - Download Pile dataset
  - `data_preprocess.py` - Tokenization and preprocessing
  - `train_transformer.py` - Full training loop (200K steps)
  - `generate_text.py` - Text generation inference
- **[sft_rlhf_guide.ipynb](sft_rlhf_guide.ipynb)** - 60+ cell educational notebook covering tokenization, dataset creation, architecture, pretraining, SFT, and RLHF

**Model Architecture:**
- 64 transformer blocks
- 2,048 embedding dimension
- 16 attention heads
- 50,304 vocabulary
- ~3B parameters

### 2. Customer Service Multi-Agent System
Production-ready AI-powered customer support automation with coordinated agent workflows:

**[customer_service_agent/](customer_service_agent/)**
- **Agents:** Intake → Router → Specialists (Billing/Technical/Sales) → QA → Escalation
- **Features:** Intent classification, priority detection, domain knowledge bases, quality validation, escalation workflow
- **Performance:** 85% success without escalation, 98% cost reduction vs human support
- **Demo:** Run with `python demo/run_demo.py`
- **Dashboard:** Interactive metrics visualization in `dashboard/dashboard.html`

### 3. Supply Chain Multi-Agent Coordinator
Intelligent logistics optimization handling complex supply chain decisions under disruption:

**[supply_chain_coordinator/](supply_chain_coordinator/)**
- **Agents:** Demand → Inventory → Logistics → Supplier → Exception Handler → Orchestrator
- **Scenarios:** 5 planning scenarios (normal, spike, disruption, capacity, combined)
- **Scope:** 3 regional warehouses, 5 SKUs, 3 suppliers, 90-day horizon
- **Performance:** $16-22K cost range, 92-99.5% fulfillment across disruption scenarios
- **Demo:** Run with `python simulation/scenario_runner.py`
- **Dashboard:** Scenario comparison and metrics in `dashboard/dashboard.html`

## 🚀 Quick Start

### LLM Training

```bash
# Install dependencies
pip install -r requirements.txt

# Download and preprocess data
python scripts/data_download.py
python scripts/data_preprocess.py

# Train transformer model
python scripts/train_transformer.py

# Generate text from checkpoint
python scripts/generate_text.py --prompt "Once upon a time"
```

### Customer Service Agent

```bash
cd customer_service_agent
pip install -r requirements.txt
python demo/run_demo.py
# Open dashboard/dashboard.html in browser
```

### Supply Chain Coordinator

```bash
cd supply_chain_coordinator
pip install -r requirements.txt
python simulation/scenario_runner.py
# Open dashboard/dashboard.html in browser
```

## 📊 Key Results

### Customer Service System
- **85%** successful resolution without escalation
- **98%** cost reduction vs human support ($0.20 AI vs $10.00 per ticket)
- **45ms** average response time
- **0.82/1.0** quality score
- Multi-domain specialist knowledge bases

### Supply Chain Coordinator
- **Cost Range:** $16,200 (normal) to $22,300 (combined disruptions)
- **Fulfillment Rate:** 92.3% - 99.5% across all scenarios
- **Robustness:** Maintains >92% fulfillment even under multiple simultaneous disruptions
- **Optimization:** 8-15% cost savings through intelligent inventory positioning

## 🏗️ Architecture Highlights

### Multi-Agent Coordination
Both automation systems demonstrate sophisticated multi-agent coordination:
- **Specialized agents** with focused responsibilities
- **Conflict resolution** through orchestrator/coordinator
- **Constraint satisfaction** handling complex overlapping requirements
- **Decision transparency** with full audit trails
- **Scalable design** easily extensible to new domains

### Model Architecture (LLM)
- **Causal self-attention** preventing future token access
- **Learned positional embeddings** up to 512 token context
- **Residual connections** in every block
- **Layer normalization** for training stability
- **Efficient data loading** from HDF5 with memory mapping

## 📖 Documentation

Each component has detailed documentation:
- [LLM Configuration Guide](config/config.py)
- [Customer Service System](customer_service_agent/README.md)
- [Supply Chain Coordinator](supply_chain_coordinator/README.md)
- [Full Jupyter Guide](sft_rlhf_guide.ipynb)

## 💡 Use Cases & Extensions

### Applicable For
- Building domain-specific language models
- Multi-agent automation for customer support
- Supply chain and operations optimization
- Demonstrating enterprise-grade agentic AI
- Fine-tuning and adaptation of language models
- Production deployment of autonomous systems

### Extension Paths
- Add retrieval-augmented generation (RAG) to agents
- Implement reinforcement learning for optimization
- Multi-task learning across agent specializations
- Distributed training for larger models
- Real-time system integration and monitoring
- Custom domain adaptation and fine-tuning

## 📝 Technologies & Dependencies

**Core:**
- Python 3.8+
- PyTorch (transformer models)
- NumPy (numerical computing)
- PyYAML (configuration)
- H5PY (data storage)
- Tiktoken (tokenization)

**Utilities:**
- Transformers library (for utilities and evaluation)
- Tokenizers (BPE implementation)

## 🙏 Acknowledgments

This project builds upon the comprehensive foundational work and methodology established by **Fareed Khan**. His original educational framework and architectural patterns provided the essential guidance for understanding and implementing transformer-based language models from scratch. The core LLM implementation directly applies his principles and structure.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details

## 🚀 Deployment & Production

For enterprise deployment:
- Customer Service: Integrate with CRM/ticketing systems via REST API
- Supply Chain: Connect to warehouse management and procurement systems
- Both: Implement monitoring, feedback loops, and continuous improvement pipelines

## 📧 Support & Contribution

This project is maintained as an educational and production showcase resource. For questions about the LLM implementation, refer to [sft_rlhf_guide.ipynb](sft_rlhf_guide.ipynb). For multi-agent system questions, see component-specific README files.

---

**Project Status:** Complete with two fully functional reference implementations and educational LLM codebase

**Last Updated:** March 2026

**Author:** aashishjain09
