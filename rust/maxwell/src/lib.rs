use std::net::TcpStream;
use std::collections::HashMap;

struct Client {
    stream: TcpStream,
}

struct Command {
    command: String,
    args: HashMap,
}

#[cfg(test)]
mod tests {
    #[test]
    fn it_connects() {
        assert_eq!(2 + 2, 4);
    }
}
