#!/usr/bin/env python3
"""
Script to update the DeltaPag profile README with repository information.
Can be run manually or via GitHub Actions.
"""

import os
import re
import sys
from pathlib import Path

try:
    from github import Github
except ImportError:
    print("Erro: PyGithub não instalado. Instale com: pip install pygithub")
    sys.exit(1)


def categorize_repo(repo):
    """Categorize a repository based on its properties."""
    repo_name = repo.name.lower()
    repo_desc = (repo.description or "").lower()
    repo_topics = [t.lower() for t in repo.get_topics()]
    
    # Check if it's a template
    if repo.is_template or 'template' in repo_name or 'template' in repo_topics:
        return 'template'
    
    # Check if it's deprecated
    if 'deprecated' in repo_name or 'deprecated' in repo_topics or 'deprecated' in repo_desc:
        return 'deprecated'
    
    # Check if it's in development
    if any(keyword in repo_name for keyword in ['wip', 'work-in-progress', 'dev', 'development']):
        return 'development'
    if any(keyword in repo_topics for keyword in ['wip', 'work-in-progress', 'in-dev', 'development']):
        return 'development'
    
    # Default to in-use
    return 'in-use'


def format_repo_markdown(repo):
    """Format a repository as markdown."""
    repo_name = repo.name
    repo_url = repo.html_url
    repo_desc = repo.description or "No description"
    repo_lang = repo.language or "N/A"
    repo_stars = repo.stargazers_count
    repo_forks = repo.forks_count
    repo_archived = repo.archived
    
    # Add archived badge if archived
    archived_badge = " 🗄️" if repo_archived else ""
    
    return (
        f"- **[{repo_name}]({repo_url})**{archived_badge} - {repo_desc}  \n"
        f"  `{repo_lang}` ⭐ {repo_stars} 🍴 {repo_forks}"
    )


def update_readme(org_name, github_token=None):
    """Update the README with repository information."""
    # Initialize GitHub client
    if github_token:
        g = Github(github_token)
    else:
        github_token = os.environ.get('GITHUB_TOKEN')
        if not github_token:
            print("Erro: Variável de ambiente GITHUB_TOKEN não definida")
            print("Você pode defini-la com: export GITHUB_TOKEN=seu_token")
            sys.exit(1)
        g = Github(github_token)
    
    # Get organization or user
    try:
        org = g.get_organization(org_name)
    except Exception:
        try:
            org = g.get_user(org_name)
        except Exception as e:
            print(f"Erro: Não foi possível encontrar a organização ou usuário '{org_name}': {e}")
            sys.exit(1)
    
    # Read current README
    script_dir = Path(__file__).parent
    readme_path = script_dir.parent / 'profile' / 'README.md'
    
    if not readme_path.exists():
        print(f"Erro: README não encontrado em {readme_path}")
        sys.exit(1)
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme_content = f.read()
    
    # Fetch all repositories
    print(f"Buscando repositórios para {org_name}...")
    repos = list(org.get_repos())
    print(f"Encontrados {len(repos)} repositórios")
    
    # Categorize repositories
    repos_in_use = []
    repos_in_dev = []
    repos_templates = []
    repos_deprecated = []
    
    for repo in repos:
        category = categorize_repo(repo)
        repo_md = format_repo_markdown(repo)
        
        if category == 'template':
            repos_templates.append(repo_md)
        elif category == 'deprecated':
            repos_deprecated.append(repo_md)
        elif category == 'development':
            repos_in_dev.append(repo_md)
        else:
            repos_in_use.append(repo_md)
    
    # If no categorization found, put all in "In Use"
    if not repos_in_use and not repos_in_dev and not repos_templates and not repos_deprecated:
        print("Nenhuma categorização encontrada, colocando todos os repositórios em 'Em Produção'")
        for repo in repos:
            repos_in_use.append(format_repo_markdown(repo))
    
    # Function to replace section
    def replace_section(content, start_marker, end_marker, new_content):
        pattern = f'({re.escape(start_marker)})(.*?)({re.escape(end_marker)})'
        replacement = f'\\1\n{new_content}\n\\3'
        return re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Replace sections
    in_use_content = '\n'.join(repos_in_use) if repos_in_use else '*Nenhum repositório nesta categoria*'
    in_dev_content = '\n'.join(repos_in_dev) if repos_in_dev else '*Nenhum repositório nesta categoria*'
    templates_content = '\n'.join(repos_templates) if repos_templates else '*Nenhum repositório nesta categoria*'
    deprecated_content = '\n'.join(repos_deprecated) if repos_deprecated else '*Nenhum repositório nesta categoria*'
    
    readme_content = replace_section(
        readme_content,
        '<!-- REPOS_IN_USE_START -->',
        '<!-- REPOS_IN_USE_END -->',
        in_use_content
    )
    
    readme_content = replace_section(
        readme_content,
        '<!-- REPOS_IN_DEVELOPMENT_START -->',
        '<!-- REPOS_IN_DEVELOPMENT_END -->',
        in_dev_content
    )
    
    readme_content = replace_section(
        readme_content,
        '<!-- REPOS_TEMPLATES_START -->',
        '<!-- REPOS_TEMPLATES_END -->',
        templates_content
    )
    
    readme_content = replace_section(
        readme_content,
        '<!-- REPOS_DEPRECATED_START -->',
        '<!-- REPOS_DEPRECATED_END -->',
        deprecated_content
    )
    
    # Update statistics
    total_repos = len(repos)
    readme_content = re.sub(
        r'!\[GitHub Org\'s repos\]\(https://img\.shields\.io/badge/Repositories-\d+-blue\)',
        f'![GitHub Org\'s repos](https://img.shields.io/badge/Repositories-{total_repos}-blue)',
        readme_content
    )
    
    # Write updated README
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"\n✅ README atualizado com {total_repos} repositórios:")
    print(f"   - Em Produção: {len(repos_in_use)}")
    print(f"   - Em Desenvolvimento: {len(repos_in_dev)}")
    print(f"   - Templates: {len(repos_templates)}")
    print(f"   - Depreciados: {len(repos_deprecated)}")


if __name__ == '__main__':
    org_name = sys.argv[1] if len(sys.argv) > 1 else 'deltapag'
    token = sys.argv[2] if len(sys.argv) > 2 else None
    update_readme(org_name, token)

