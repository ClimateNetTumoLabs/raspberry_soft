# AutoDeploy Workflow
This repository contains a GitHub Actions workflow (`deploy.yml`) that enables automatic deployment to a remote server whenever code is pushed to the `main` branch. The workflow uses SSH to securely access the server and perform a `git pull` operation in the specified repository directory.

## Setting Up Secrets
Before you can use this workflow, you need to set up the required secrets in your GitHub repository. Secrets are used to securely store sensitive information like SSH keys and server credentials. To set up the secrets, follow these steps:

1. In your GitHub repository, go to "Settings" > "Secrets" > "New repository secret".
2. Create the following secrets:
    * `EC2_PRIVATE_KEY`: The private PEM key to authenticate with the remote server.
    * `EC2_IP`: The IP address or hostname of the remote server.
    * `EC2_USERNAME`: The username used to log in to the remote server.

## Server SSH Key Setup
1. On the remote server, generate an SSH key pair using the following command:

   ```bash
   ssh-keygen -t rsa
   ```

   This will generate a private key `id_rsa` and a corresponding public key `id_rsa.pub` in the ~/.ssh directory.

2. Add the public key to your GitHub repository as a deploy key:
    
   * Go to your GitHub repository and navigate to "Settings" > "Deploy keys" > "Add deploy key".
   * Give the key a title (e.g., "ES2 Server key").
   * Copy the contents of the id_rsa.pub file on the server and paste it into the key field.
   * Check the box for "Allow write access" if you need write permissions.

## Workflow Execution
When a push is made to the `main` branch, the workflow will automatically execute the following steps:

1. It retrieves the required secrets: `EC2_PRIVATE_KEY`, `EC2_IP`, and `EC2_USERNAME`.
2. It creates the `private_key.pem` file from the `EC2_PRIVATE_KEY` secret and sets the appropriate permissions.
3. It establishes an SSH connection to the remote server using the private key and username provided.
4. It navigates to the specified repository directory on the server (`/home/ubuntu/REPOSITORY_PATH`).
5. It checks out the `main` branch and performs a `git pull` to update the codebase.

## Configuration
To use this workflow in your repository, follow these steps:

1. Create a directory named `.github/workflows` in the root of your repository if it doesn't exist.
2. Place the `deploy.yml` file provided above into the `.github/workflows` directory.
3. If the repository directory does not exist on the server, clone the repository using the following command:
   
   ```bash
   git clone REPOSITORY_URL
   ```
4. Make sure to replace `/home/ubuntu/REPOSITORY_PATH` with the actual path to your project's directory on the remote server.

By using this GitHub Actions workflow, you can streamline your deployment process and ensure that your code is automatically updated on the remote server whenever changes are pushed to the `main` branch.
