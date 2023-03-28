Perform Rust cargo command.

This executes given cargo command in a Rust project.

**Role Variables**

.. zuul:role_var:: rust_cargo_executable
   :default: cargo

   Path to `cargo` executable

.. zuul:role_var:: rust_cargo_command
   :default: build

   Cargo command to be executed
