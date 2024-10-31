
  create or replace   view homework3.analytics.my_second_dbt_model
  
   as (
    -- Use the `ref` function to select from other models

select *
from homework3.analytics.my_first_dbt_model
where id = 1
  );

