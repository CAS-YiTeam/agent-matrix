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
    # 遵从虚幻引擎C++的命名规范
    USTRUCT(BlueprintType)
    struct FMatrixMsgStruct
    {

        GENERATED_BODY()


        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString Src;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString Dst;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString Command;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString Arg;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString Kwargs;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        bool NeedReply;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString ReservedField_01;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString ReservedField_02;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString ReservedField_03;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString ReservedField_04;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString ReservedField_05;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString ReservedField_06;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString ReservedField_07;

        UPROPERTY(EditDefaultsOnly, BlueprintReadWrite)
        FString ReservedField_08;
    };
    """

    Src: str
        # source agent id

    Dst: str
        # destination agent id

    Command: str
        # enum "connect_to_matrix"
        # enum "agent_activate"

    Arg: str

    Kwargs: str

    NeedReply: bool = False

    ReservedField_01: str

    ReservedField_02: str

    ReservedField_03: str

    ReservedField_04: str

    ReservedField_05: str

    ReservedField_06: str

    ReservedField_07: str

    ReservedField_08: str
