
  create or replace   view homework3.analytics.user_session_channel
  
   as (
    WITH filtered_user_sessions AS (
    SELECT
        userId,
        sessionId,
        channel
    FROM homework3.raw_data.user_session_channel
    WHERE sessionId IS NOT NULL
)
SELECT * FROM filtered_user_sessions
  );

