delete from question_tag;
delete from tag;


insert into tag values(1, 'java');
insert into tag values(2, 'html');
insert into tag values(3, 'css');
insert into tag values(4, 'python');
insert into tag values(5, 'c#');
insert into tag values(6, 'c++');
insert into tag values(7, 'javascript');
insert into tag values(8, 'sql');
insert into tag values(9, 'general');


insert into question_tag(question_id, tag_id)
select question.id, tag.id
from question, tag
where tag.id = 5;


----------------01.02.21

ALTER TABLE question
ADD user_name varchar;
update question
set user_name = 'user';

ALTER TABLE answer
ADD user_name varchar;
update answer
set user_name = 'user';

ALTER TABLE comment
ADD user_name varchar;
update comment
set user_name = 'user';
