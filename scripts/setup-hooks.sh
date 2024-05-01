#!/bin/bash

# Path to the Git hooks folder
HOOKS_DIR=".git/hooks"

# Creating the pre-push hook
cat > $HOOKS_DIR/pre-push << 'EOF'
#!/bin/sh
echo "Running tests before push..."
pytest
if [ $? -ne 0 ]; then
  echo "Tests failed, aborting push."
  exit 1
fi
echo "Tests passed, push will proceed."
EOF

# Make the hook executable
chmod +x $HOOKS_DIR/pre-push

echo "Git hooks set up successfully."
