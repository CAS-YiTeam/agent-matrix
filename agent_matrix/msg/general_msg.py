from datetime import datetime
from typing import List, Optional, Any
from pydantic import BaseModel

class GeneralMsg(BaseModel):
    src: str
        # source agent id

    dst: str
        # destination agent id

    command: str
        # enum "connect_to_matrix"
        # enum "agent_activate"

    need_reply: bool = False

    kwargs: dict = {}


class UserInterfaceMsg(BaseModel):
    """
    USTRUCT(BlueprintType)
    struct FMatrixMsgStruct
    {

        GENERATED_BODY()

        // 必须使用小写字母 + 下划线！
        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString src;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString dst;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString command;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString arg;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString kwargs;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        bool need_reply;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString reserved_field_01;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString reserved_field_02;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString reserved_field_03;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString reserved_field_04;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString reserved_field_05;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString reserved_field_06;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString reserved_field_07;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString reserved_field_08;
    };
    """

    src: str
        # source agent id

    dst: str
        # destination agent id

    command: str
        # enum "connect_to_matrix"
        # enum "agent_activate"

    arg: str

    kwargs: str

    need_reply: bool = False

    reserved_field_01: str

    reserved_field_02: str

    reserved_field_03: str

    reserved_field_04: str

    reserved_field_05: str

    reserved_field_06: str

    reserved_field_07: str

    reserved_field_08: str
