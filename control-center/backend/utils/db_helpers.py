"""
Database query optimization helpers

Provides utilities for:
- Eager loading with SQLAlchemy (joinedload, selectinload)
- Query optimization patterns
- N+1 query prevention
- Efficient relationship loading
"""

from typing import Any, Dict, List, Optional, Type, TypeVar
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload, joinedload, contains_eager
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Base, Agent, KnowledgeFile, Service

# Generic type for models
ModelType = TypeVar("ModelType", bound=Base)


class QueryOptimizer:
    """
    Helper class for optimized database queries

    Provides methods to prevent N+1 queries and optimize data loading
    """

    @staticmethod
    async def get_agents_with_knowledge(
        session: AsyncSession,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Agent]:
        """
        Get agents with their knowledge files eagerly loaded (prevents N+1)

        Args:
            session: Database session
            limit: Optional limit
            offset: Optional offset

        Returns:
            List of Agent objects with knowledge_files loaded
        """
        query = select(Agent).options(
            selectinload(Agent.knowledge_files)
        )

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_agent_with_knowledge(
        session: AsyncSession,
        agent_id: int
    ) -> Optional[Agent]:
        """
        Get single agent with knowledge files eagerly loaded

        Args:
            session: Database session
            agent_id: Agent ID

        Returns:
            Agent object with knowledge_files loaded, or None
        """
        query = select(Agent).options(
            selectinload(Agent.knowledge_files)
        ).where(Agent.id == agent_id)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_agents_by_category(
        session: AsyncSession,
        category: str,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Agent]:
        """
        Get agents by category with knowledge files

        Args:
            session: Database session
            category: Agent category
            limit: Optional limit
            offset: Optional offset

        Returns:
            List of Agent objects
        """
        query = select(Agent).options(
            selectinload(Agent.knowledge_files)
        ).where(Agent.category == category)

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def count_agents(
        session: AsyncSession,
        category: Optional[str] = None
    ) -> int:
        """
        Count agents, optionally filtered by category

        Args:
            session: Database session
            category: Optional category filter

        Returns:
            Count of agents
        """
        query = select(func.count(Agent.id))

        if category:
            query = query.where(Agent.category == category)

        result = await session.execute(query)
        return result.scalar()

    @staticmethod
    async def get_knowledge_files_with_agents(
        session: AsyncSession,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[KnowledgeFile]:
        """
        Get knowledge files with their agents eagerly loaded

        Args:
            session: Database session
            limit: Optional limit
            offset: Optional offset

        Returns:
            List of KnowledgeFile objects with agent loaded
        """
        query = select(KnowledgeFile).options(
            joinedload(KnowledgeFile.agent)
        )

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await session.execute(query)
        return result.unique().scalars().all()

    @staticmethod
    async def get_knowledge_files_by_agent(
        session: AsyncSession,
        agent_id: int,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[KnowledgeFile]:
        """
        Get knowledge files for a specific agent

        Args:
            session: Database session
            agent_id: Agent ID
            limit: Optional limit
            offset: Optional offset

        Returns:
            List of KnowledgeFile objects
        """
        query = select(KnowledgeFile).where(
            KnowledgeFile.agent_id == agent_id
        )

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def count_knowledge_files(
        session: AsyncSession,
        agent_id: Optional[int] = None
    ) -> int:
        """
        Count knowledge files, optionally filtered by agent

        Args:
            session: Database session
            agent_id: Optional agent ID filter

        Returns:
            Count of knowledge files
        """
        query = select(func.count(KnowledgeFile.id))

        if agent_id:
            query = query.where(KnowledgeFile.agent_id == agent_id)

        result = await session.execute(query)
        return result.scalar()

    @staticmethod
    async def get_services(
        session: AsyncSession,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[Service]:
        """
        Get services with pagination

        Args:
            session: Database session
            limit: Optional limit
            offset: Optional offset

        Returns:
            List of Service objects
        """
        query = select(Service)

        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def count_services(session: AsyncSession) -> int:
        """
        Count services

        Args:
            session: Database session

        Returns:
            Count of services
        """
        query = select(func.count(Service.id))
        result = await session.execute(query)
        return result.scalar()

    @staticmethod
    async def get_agent_stats(session: AsyncSession) -> Dict[str, Any]:
        """
        Get agent statistics with optimized queries

        Args:
            session: Database session

        Returns:
            Dictionary with agent statistics
        """
        # Count agents by category (single query with GROUP BY)
        from sqlalchemy import func

        category_query = select(
            Agent.category,
            func.count(Agent.id).label('count')
        ).group_by(Agent.category)

        category_result = await session.execute(category_query)
        categories = {row.category: row.count for row in category_result}

        # Count agents by level (single query with GROUP BY)
        level_query = select(
            Agent.level,
            func.count(Agent.id).label('count')
        ).group_by(Agent.level)

        level_result = await session.execute(level_query)
        levels = {row.level: row.count for row in level_result}

        # Total count
        total_query = select(func.count(Agent.id))
        total_result = await session.execute(total_query)
        total = total_result.scalar()

        return {
            "total": total,
            "by_category": categories,
            "by_level": levels
        }

    @staticmethod
    async def bulk_create_knowledge_files(
        session: AsyncSession,
        knowledge_files: List[Dict[str, Any]]
    ) -> int:
        """
        Bulk create knowledge files (more efficient than one-by-one)

        Args:
            session: Database session
            knowledge_files: List of knowledge file data dictionaries

        Returns:
            Number of files created
        """
        objects = [KnowledgeFile(**data) for data in knowledge_files]
        session.add_all(objects)
        await session.flush()
        return len(objects)

    @staticmethod
    async def bulk_create_agents(
        session: AsyncSession,
        agents: List[Dict[str, Any]]
    ) -> int:
        """
        Bulk create agents (more efficient than one-by-one)

        Args:
            session: Database session
            agents: List of agent data dictionaries

        Returns:
            Number of agents created
        """
        objects = [Agent(**data) for data in agents]
        session.add_all(objects)
        await session.flush()
        return len(objects)


# Convenience functions for common patterns

async def get_paginated_query(
    session: AsyncSession,
    model: Type[ModelType],
    page: int = 1,
    page_size: int = 50,
    filters: Optional[Dict[str, Any]] = None,
    order_by: Optional[Any] = None,
    eager_load: Optional[List[Any]] = None
) -> tuple[List[ModelType], int]:
    """
    Generic paginated query helper

    Args:
        session: Database session
        model: SQLAlchemy model class
        page: Page number (1-indexed)
        page_size: Items per page
        filters: Optional dictionary of filters {column: value}
        order_by: Optional order by clause
        eager_load: Optional list of relationships to eager load

    Returns:
        Tuple of (items, total_count)
    """
    # Build base query
    query = select(model)

    # Add eager loading
    if eager_load:
        for relationship in eager_load:
            query = query.options(selectinload(relationship))

    # Add filters
    if filters:
        for column, value in filters.items():
            query = query.where(getattr(model, column) == value)

    # Add ordering
    if order_by is not None:
        query = query.order_by(order_by)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await session.execute(count_query)
    total = total_result.scalar()

    # Add pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)

    # Execute query
    result = await session.execute(query)
    items = result.scalars().all()

    return items, total


# Export optimizer instance for convenience
optimizer = QueryOptimizer()
