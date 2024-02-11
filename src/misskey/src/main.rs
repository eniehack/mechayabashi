use std::collections::HashMap;

use clap::Parser;
use sqlx::{sqlite::SqlitePoolOptions, SqlitePool};
use rand::{prelude::*, Rng, seq::SliceRandom};

const BEGIN: &str = "__BEGIN__";
const END: &str = "__END__";

#[derive(sqlx::FromRow, Debug)]
struct Word {
    word: String,
    frequency: i64,
    feedback: f64,
}

enum AppError {
    SqlError(String),
    UnknownErr
}

async fn choice_token<R: Rng + ?Sized>(conn: &SqlitePool, rng: &mut R, sentence: Vec<String>) -> Result<String, AppError> {
    let arg = sentence.join(" ") + " %";
    let resp = sqlx::query_as!(
        Word,
        "SELECT word, frequency, feedback FROM words WHERE word LIKE ?",
        arg
    )
        .fetch_all(conn)
        .await;

    match resp {
        Ok(words) => {
            let r: f32 = rng.gen();
            if r < 0.334 {
                let token = words.choose(rng).unwrap();
                if let Some(next) = token.word.split_whitespace().collect::<Vec<&str>>().last() {
                    return Ok(next.to_string())
                } else {
                    return Err(AppError::UnknownErr)
                }
            } else {
                let token = words.choose_weighted(rng, |item| (item.feedback + (item.frequency as f64)) / words.len() as f64).unwrap();
                if let Some(next) = token.word.split_whitespace().collect::<Vec<&str>>().last() {
                    return Ok(next.to_string())
                } else {
                    return Err(AppError::UnknownErr)
                }
            }
        }
        Err(e) => Err(AppError::SqlError(e.to_string()))
    }
}

async fn generate_text<R: Rng + ?Sized>(db: &SqlitePool, rng: &mut R, state: u16) -> String {
    let usize_state = usize::try_from(state).unwrap();
    let mut sentence: Vec<String> = Vec::new();
    for _ in 0..state {
        sentence.push(BEGIN.to_string());
    }
    while END.to_string() != sentence[sentence.len() - usize_state] {
        if let Ok(token) = choice_token(db, rng, sentence[(sentence.len() - usize_state)..sentence.len()].to_vec()).await {
            sentence.push(token.clone());
        }
        println!("{:?}", sentence);
    }
    return sentence
        .iter()
        .fold(String::new(), |acc, x| {
            if *x == BEGIN.to_string() || *x == END.to_string() {
                return acc;
            }
            acc + x
        });
}

#[derive(Parser)]
struct AppArgs {
    #[clap(long)]
    server: String,
    #[clap(long)]
    token: String,
    #[clap(long)]
    db: String,
    #[clap(long)]
    state: u16,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>>{
    let args = AppArgs::parse();
    let db_url = format!("sqlite://{}", args.db).to_string();
    let mut db = SqlitePoolOptions::new()
        .connect(&db_url)
        .await?;
    let mut rng = rand::thread_rng();

    let mut map = HashMap::new();
    map.insert("i", args.token.to_owned());
    map.insert("text", generate_text(&mut db, &mut rng, args.state).await);
    map.insert("visibility", "home".to_string());

    let client = reqwest::Client::new();
    let _resp = client.post(format!("https://{}/api/notes/create", args.server))
        .json(&map)
        .send()
        .await?;
    Ok(())
}
