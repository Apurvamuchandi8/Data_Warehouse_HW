
  
    

        create or replace transient table homework3.analytics.session_summary
         as
        (WITH  __dbt__cte__user_session_channel as (
WITH filtered_user_sessions AS (
    SELECT
        userId,
        sessionId,
        channel
    FROM homework3.raw_data.user_session_channel
    WHERE sessionId IS NOT NULL
)
SELECT * FROM filtered_user_sessions
),  __dbt__cte__session_timestamp as (
WITH filtered_session_timestamp AS (
    SELECT
        sessionId,
        ts
    FROM homework3.raw_data.session_timestamp
    WHERE sessionId IS NOT NULL
)
SELECT * FROM filtered_session_timestamp
), u AS (
SELECT * FROM __dbt__cte__user_session_channel
), st AS (
SELECT * FROM __dbt__cte__session_timestamp
)
SELECT u.userId, u.sessionId, u.channel, st.ts
FROM u
JOIN st ON u.sessionId = st.sessionId
        );
      
  