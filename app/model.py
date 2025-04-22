import json
import logging
import os
import sys
import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments, get_linear_schedule_with_warmup
from datasets import Dataset
import traceback
from sklearn.metrics import accuracy_score, precision_recall_fscore_support

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("D:/IVR Case-02/training.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Define save directory
save_dir = "D:/IVR Case-02/banking-intents-minilm"
logger.info(f"Using save directory: {save_dir}")

# Check directory
try:
    logger.info(f"Creating/checking save directory: {save_dir}")
    os.makedirs(save_dir, exist_ok=True)
    test_file = os.path.join(save_dir, "test.txt")
    with open(test_file, "w") as f:
        f.write("test")
    os.remove(test_file)
    logger.info("Directory is writable")
except Exception as e:
    logger.error(f"Directory error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Load dataset
csv_path = "D:/IVR Case-02/app/data/banking_intents.csv"
try:
    logger.info(f"Loading dataset from {csv_path}")
    df = pd.read_csv(csv_path)

    logger.info("Class distribution (before balancing):")
    logger.info(df["intent"].value_counts())

    if not {"query", "intent"}.issubset(df.columns):
        logger.error("Dataset missing 'query' or 'intent' columns")
        raise ValueError("CSV must have 'query' and 'intent' columns")
    if df["query"].isnull().any() or df["intent"].isnull().any():
        logger.error("Dataset contains null values")
        raise ValueError("Dataset contains null values")
    logger.info(f"Dataset loaded with {len(df)} rows")
    logger.info(f"Unique intents: {len(df['intent'].unique())}")
except Exception as e:
    logger.error(f"Dataset load error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Balance classes by oversampling
try:
    logger.info("Balancing classes")
    intent_counts = df["intent"].value_counts()
    max_count = intent_counts.max()  # Target ~40 samples per intent
    balanced_data = {"query": [], "intent": []}
    for intent in df["intent"].unique():
        intent_df = df[df["intent"] == intent]
        if len(intent_df) < max_count:
            oversampled = intent_df.sample(n=max_count - len(intent_df), replace=True, random_state=42)
            balanced_data["query"].extend(intent_df["query"].tolist() + oversampled["query"].tolist())
            balanced_data["intent"].extend([intent] * max_count)
        else:
            balanced_data["query"].extend(intent_df["query"].tolist())
            balanced_data["intent"].extend([intent] * len(intent_df))
    df = pd.DataFrame(balanced_data)
    logger.info("Class distribution (after balancing):")
    logger.info(df["intent"].value_counts())
    logger.info(f"Balanced dataset size: {len(df)}")
except Exception as e:
    logger.error(f"Class balancing error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Encode labels
try:
    logger.info("Encoding labels")
    labels = sorted(df["intent"].unique())
    label2id = {label: idx for idx, label in enumerate(labels)}
    id2label = {idx: label for label, idx in label2id.items()}
    df["label"] = df["intent"].map(label2id)
    logger.info(f"Labels: {labels}")
    logger.info(f"Label2id: {label2id}")
except Exception as e:
    logger.error(f"Label encoding error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Initialize tokenizer and model
model_name = "distilbert-base-uncased"
try:
    logger.info(f"Loading model: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(labels),
        id2label=id2label,
        label2id=label2id
    )
    logger.info("Model and tokenizer loaded")
except Exception as e:
    logger.error(f"Model load error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Tokenization function
def tokenize_function(batch):
    return tokenizer(batch["query"], padding="max_length", truncation=True, max_length=256)

# Convert to Dataset
try:
    logger.info("Converting to Hugging Face Dataset")
    dataset = Dataset.from_pandas(df)
    logger.info(f"Dataset columns: {dataset.column_names}")
    dataset = dataset.map(tokenize_function, batched=True)
    dataset = dataset.train_test_split(test_size=0.2, seed=42)
    dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])
    logger.info(f"Train dataset size: {len(dataset['train'])}")
    logger.info(f"Test dataset size: {len(dataset['test'])}")
except Exception as e:
    logger.error(f"Dataset processing error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Compute metrics
def compute_metrics(pred):
    labels = pred.label_ids
    preds = pred.predictions.argmax(-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average='weighted')
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc,
        'f1': f1,
        'precision': precision,
        'recall': recall
    }

# Define training arguments
try:
    logger.info("Setting training arguments")
    training_args = TrainingArguments(
        output_dir=save_dir,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=10,  # Increased for better convergence
        learning_rate=3e-5,
        weight_decay=0.01,
        logging_dir="D:/IVR Case-02/logs",
        logging_steps=10,
        do_eval=True,  # Enable evaluation at epoch boundaries
        save_strategy="epoch",  # Save at epoch boundaries
        save_total_limit=1
    )
except Exception as e:
    logger.error(f"Training args error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Initialize Trainer
try:
    logger.info("Initializing Trainer")
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset["train"],
        eval_dataset=dataset["test"],
        tokenizer=tokenizer,
        compute_metrics=compute_metrics
    )
except Exception as e:
    logger.error(f"Trainer init error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Configure learning rate scheduler
try:
    num_training_steps = len(trainer.train_dataset) * training_args.num_train_epochs // training_args.per_device_train_batch_size
    warmup_steps = int(0.1 * num_training_steps)
    optimizer = torch.optim.AdamW(model.parameters(), lr=training_args.learning_rate, weight_decay=training_args.weight_decay)
    lr_scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=warmup_steps,
        num_training_steps=num_training_steps
    )
    trainer.optimizer = optimizer
    trainer.lr_scheduler = lr_scheduler
except Exception as e:
    logger.error(f"LR Scheduler setup error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Train the model
try:
    logger.info("Starting training")
    trainer.train()
    logger.info("Training complete")
    eval_results = trainer.evaluate()
    logger.info(f"Final evaluation results: {eval_results}")
except Exception as e:
    logger.error(f"Training error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Save the model explicitly
try:
    logger.info(f"Saving model to {save_dir}")
    trainer.save_model(save_dir)
    tokenizer.save_pretrained(save_dir)
    logger.info("Checking saved files after trainer.save_model")
    saved_files = os.listdir(save_dir)
    logger.info(f"Saved files: {saved_files}")
    model_bin_path = os.path.join(save_dir, "pytorch_model.bin")
    if not os.path.exists(model_bin_path):
        logger.warning("pytorch_model.bin not found, attempting direct model save")
        torch.save(model.state_dict(), model_bin_path)
        logger.info("Model saved directly via torch.save")
    saved_files = os.listdir(save_dir)
    logger.info(f"Updated saved files: {saved_files}")
    if "pytorch_model.bin" not in saved_files:
        logger.error("pytorch_model.bin still not found in save_dir")
        raise FileNotFoundError("pytorch_model.bin not saved in save_dir")
    logger.info("pytorch_model.bin successfully saved")
except Exception as e:
    logger.error(f"Save error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

# Save label mappings
try:
    logger.info("Saving label mappings")
    with open(os.path.join(save_dir, "label2id.json"), "w") as f:
        json.dump(label2id, f)
    with open(os.path.join(save_dir, "id2label.json"), "w") as f:
        json.dump(id2label, f)
    logger.info("Label mappings saved")
except Exception as e:
    logger.error(f"Label saving error: {str(e)}")
    logger.error(traceback.format_exc())
    raise

logger.info("Process completed successfully")